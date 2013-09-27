"""
This is an example plugin which can listen for 
events and register new config options.
"""

try:

	from actr6_jni import Dispatcher, JNI_Server, VisualChunk
	import pygame
	import pygl2d
	import webcolors
	
	def RenderTextToChunk(name, text, rect):
		return VisualChunk(name, "text", rect.centerx, rect.centery, 
						   rect.width, rect.height, webcolors.rgb_to_name(text.color),
						   value=text.text)
		
	def ShipToChunk(ship):
		return VisualChunk("ship", "visual-object", ship.position.x, ship.position.y,
						   ship.get_width(), ship.get_height(), color="yellow")
		
	class SF5Plugin(object):
	
		d = Dispatcher()
	
		name = 'ACT-R'
		
		def __init__(self, app):
			super(SF5Plugin, self).__init__()
			self.app = app
			self.actr = None
			
		def ready(self):
			if self.app.config[self.name]['enabled']:
				self.actr = JNI_Server(self)
				self.actr.addDispatcher(self.d)
				self.app.reactor.listenTCP(int(self.app.config[self.name]['port']), self.actr)
				self.app.state = self.app.STATE_WAIT_CONNECT
				
		##################################################################
		# Handle game events
		##################################################################
			
		def eventCallback(self, *args, **kwargs):
		
			if args[3] == 'config' and args[4] == 'load':
			
				if args[5] == 'defaults':
					self.app.config.add_setting(self.name, 'enabled', False, type=2, alias="Enable", about='Enable ACT-R model support')
					self.app.config.add_setting(self.name, 'port', '5555', type=3, alias="Incoming Port", about='ACT-R JNI Port')
			
			if args[3] == 'session' and args[4] == 'ready':
				self.actr_waiting = pygl2d.font.RenderText('Waiting for ACT-R', (255, 0, 0), self.app.font2)
				self.actr_waiting_rect = self.actr_waiting.get_rect()
				self.actr_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)
				self.model_waiting = pygl2d.font.RenderText('Waiting for Model', (0, 255, 0), self.app.font2)
				self.model_waiting_rect = self.model_waiting.get_rect()
				self.model_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)
				
			if args[3] == 'game' and args[4] == 'setstate':
			
				if args[5] == self.app.STATE_GAMENO:
					self.actr.display_new([RenderTextToChunk(None,self.app.game_title,self.app.game_title_rect)])
				elif args[5] == self.app.STATE_IFF:
					chunks = [RenderTextToChunk(None,foe[0],foe[1]) for foe in self.app.foe_letters]
					chunks += [
							RenderTextToChunk(None,self.app.foe_top,self.app.foe_top_rect),
							RenderTextToChunk(None,self.app.foe_midbot,self.app.foe_midbot_rect),
							RenderTextToChunk(None,self.app.foe_bottom,self.app.foe_bottom_rect)
							]
					self.actr.display_new(chunks)
				elif args[5] == self.app.STATE_PLAY:
					chunks = [ShipToChunk(self.app.ship)]
					self.actr.display_new(chunks)
			
			if args[3] == 'score+' and args[4] == 'pnts':
				self.actr.trigger_reward(args[5])
			if args[3] == 'score-' and args[4] == 'pnts':
				self.actr.trigger_reward(args[5])
			
			if args[3] == 'press' and args[5] == 'user' and args[4] == pygame.K_ESCAPE:
				self.actr.trigger_event(":break")
					
			if args[3] == 'display' and args[4] == 'preflip':
				
				if self.app.state == self.app.STATE_WAIT_CONNECT:
					self.draw_actr_wait_msg()
				elif self.app.state == self.app.STATE_WAIT_MODEL:
					self.draw_model_wait_msg()
				elif self.app.state == self.app.STATE_PLAY:
					chunks = [ShipToChunk(self.app.ship)]
					self.actr.display_update(chunks)
						
					#else if self.app.state == self.app.STATE_PLAY:
					#	 result = []
					#	 if self.app.fortress_exists and self.app.fortress.alive:
					#		 result.append(self.app.fortress.FortresstoChunk())
					#	 if self.app.ship.alive:
					#		 result.append(self.app.ship.ShiptoChunk())
				   #	if result:
				   #		self.app.actr.update_display(result)
						
		
		##################################################################
		# Misc routines
		##################################################################
		
		def draw_actr_wait_msg(self):
			"""Display Waiting for ACT-R msg"""
			self.actr_waiting.draw(self.actr_waiting_rect.topleft)
		
		def draw_model_wait_msg(self):
			"""Display Waiting for Model msg"""
			self.model_waiting.draw(self.model_waiting_rect.topleft)
						
		##################################################################
		# Begin JNI Callbacks
		##################################################################
						
		@d.listen('connectionMade')
		def ACTR6_JNI_Event(self, model, params):
			print("Connection Made")
			self.app.setState(self.app.STATE_WAIT_MODEL)
			self.app.current_game = 0
			
		@d.listen('connectionLost')
		def ACTR6_JNI_Event(self, model, params):
			print("Connection Lost")
			self.app.setState(self.app.STATE_WAIT_CONNECT)
		   
		@d.listen('reset')
		def ACTR6_JNI_Event(self, model, params):
			print("Reset")
			self.app.setState(self.app.STATE_WAIT_MODEL)
			self.app.current_game = 0
	
		@d.listen('model-run')
		def ACTR6_JNI_Event(self, model, params):
			print ("model-run") 
			if not params['resume']:
				self.app.setState(self.app.STATE_SETUP)
			self.actr_running = True
	
		@d.listen('model-stop')
		def ACTR6_JNI_Event(self, model, params):
			print("model-stop")
			#self.state = self.STATE_SCORES
	
		@d.listen('keypress')
		def ACTR6_JNI_Event(self, model, params):
			print("keypress",  params['keycode'], chr(params['keycode']))
			key = params['keycode']
			if key == 10:
				key = 13
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":key}))
			self.app.reactor.callLater(.02, pygame.event.post, pygame.event.Event(pygame.KEYUP, {"key":key}))
	
		@d.listen('mousemotion')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress
	
		@d.listen('mouseclick')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress

except ImportError as e:
	sys.stderr.write("Failed to load 'ACT-R JNI' plugin, missing dependencies. [%s]\n" % e)
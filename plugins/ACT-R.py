"""
This is an example plugin which can listen for 
events and register new config options.
"""

try:

	import sys
	from actr6_jni import Dispatcher, JNI_Server, VisualChunk
	import pygame
	import pygl2d
	import webcolors
	
	class TokenChunk(VisualChunk):
		
		def get_visual_location(self):
			chunk = super(TokenChunk, self).get_visual_location()
			chunk["isa"] = "token-location"
			for s, v in self.slots.iteritems():
				if s in ["orientation", "velocity"]:
					chunk["slots"][s] = v
			return chunk
	
	def RenderTextToChunk(name, text, rect):
		return VisualChunk(name, "text", rect.centerx, rect.centery, 
						rect.width, rect.height, webcolors.rgb_to_name(text.color),
						value=text.text)
		
	def ShipToChunk(ship):
		return TokenChunk("ship", "ship", ship.position.x, ship.position.y,
						ship.get_width(), ship.get_height(), color="yellow",
						orientation=ship.orientation, velocity=ship.get_velocity())
	
	def FortressToChunk(fortress):
		return TokenChunk("fortress", "fortress", fortress.position.x, fortress.position.y,
						fortress.get_width(), fortress.get_height(), color="yellow",
						orientation=fortress.orientation, velocity=fortress.get_velocity())
		
	def ShellToChunk(shell):
		return TokenChunk("shell%d" % shell._id, "shell", shell.position.x, shell.position.y,
						shell.get_width(), shell.get_height(), color="red",
						orientation=shell.orientation, velocity=shell.get_velocity())

	def MissileToChunk(missile):
		return TokenChunk("missile%d" % missile._id, "missile", missile.position.x, missile.position.y,
						missile.get_width(), missile.get_height(), color="red",
						orientation=missile.orientation, velocity=missile.get_velocity())
				
	def MineToChunk(mine):
		return TokenChunk("mine%d" % mine._id, "mine", mine.position.x, mine.position.y,
						mine.get_width(), mine.get_height(), color="red",
						orientation=mine.orientation, velocity=mine.get_velocity())
		
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
			
			
			if self.actr:
			
				if args[3] == 'session':
					
					if args[4] == 'ready':
						self.actr_waiting = pygl2d.font.RenderText('Waiting for ACT-R', (255, 0, 0), self.app.font2)
						self.actr_waiting_rect = self.actr_waiting.get_rect()
						self.actr_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)
						self.model_waiting = pygl2d.font.RenderText('Waiting for Model', (0, 255, 0), self.app.font2)
						self.model_waiting_rect = self.model_waiting.get_rect()
						self.model_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)
					
				elif args[3] == 'game':
					
					if args[4] == 'setstate':
				
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
							if not self.resume:
								chunks = [ShipToChunk(self.app.ship)]
								if self.app.fortress_exists:
									chunks.append(FortressToChunk(self.app.fortress))
								self.actr.display_new(chunks)
				
				elif args[3] == 'score+':
					if args[4] == 'pnts':
						self.actr.trigger_reward(args[5])
				elif args[3] == 'score-':
					if args[4] == 'pnts':
						self.actr.trigger_reward(-args[5])
				
				elif args[3] == 'press':
					if args[5] == 'user':
						if args[4] == pygame.K_ESCAPE:
							self.actr.trigger_event(":break")
							
				elif args[3] == 'fire':
					
					if args[4] == 'fortress':
						self.actr.display_add(ShellToChunk(self.app.shell_list[-1]))

				elif args[3] == 'shell':
					
					if args[4] == 'removed':
						
						self.actr.display_remove(name="shell%d-loc" % args[5])
						
				elif args[3] == 'display':
					
					if args[4] == 'preflip':
					
						if self.app.state == self.app.STATE_WAIT_CONNECT:
							self.draw_actr_wait_msg()
						elif self.app.state == self.app.STATE_WAIT_MODEL:
							self.draw_model_wait_msg()
						elif self.app.state == self.app.STATE_PLAY:
							chunks = [ShipToChunk(self.app.ship)]
							if self.app.fortress_exists:
								chunks.append(FortressToChunk(self.app.fortress))
								for shell in self.app.shell_list:
									chunks.append(ShellToChunk(shell))
							self.actr.display_update(chunks)
						
		
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
			if params['resume']:
				self.resume = True
				self.app.setState(self.app.STATE_PLAY)
				self.app.gametimer.unpause()
			else:
				self.resume = False
				self.app.setState(self.app.STATE_SETUP)
	
		@d.listen('model-stop')
		def ACTR6_JNI_Event(self, model, params):
			print("model-stop")
			self.app.gametimer.pause()
			self.app.setState(self.app.STATE_PAUSED)

		@d.listen('hold-finger')
		def ACTR6_JNI_Event(self, model, params):
			hand = params['hand']
			finger = params['finger']
			if hand == "LEFT":
				if finger == "MIDDLE":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('w')}))
				elif finger == "RING":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('a')}))
				elif finger == "INDEX":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('d')}))
			elif hand == "RIGHT":
				if finger == "INDEX":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('j')}))
				elif finger == "MIDDLE":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('k')}))
				elif finger == "RING":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('l')}))
				elif finger == "PINKY":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord('\r')}))
				elif finger == "THUMB":
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":ord(' ')}))
					
		@d.listen('release-finger')
		def ACTR6_JNI_Event(self, model, params):
			hand = params['hand']
			finger = params['finger']
			if hand == "LEFT":
				if finger == "MIDDLE":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('w')}))
				elif finger == "RING":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('a')}))
				elif finger == "INDEX":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('d')}))
			elif hand == "RIGHT":
				if finger == "INDEX":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('j')}))
				elif finger == "MIDDLE":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('k')}))
				elif finger == "RING":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('l')}))
				elif finger == "PINKY":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord('\r')}))
				elif finger == "THUMB":
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":ord(' ')}))
	
		@d.listen('mousemotion')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress
	
		@d.listen('mouseclick')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress

except ImportError as e:
	sys.stderr.write("Failed to load 'ACT-R JNI' plugin, missing dependencies. [%s]\n" % e)
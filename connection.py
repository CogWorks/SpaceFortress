import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

class DBus_obj(dbus.service.Object):

    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def HelloWorld(self, hello_message):
        print "Got the message \'%s\'"%hello_message
        return "I received your kind message"
        
DBusGMainLoop(set_as_default=True) #must do this before connecting to the bus
= webyay
Web based Yaesu (FT-991A) CAT control


== Overview

The idea here is to allow full control of an FT-991A from a web browser without any extra software, and no hardware other than a USB connection.

The FT-991A has both serial and audio over USB.  WebSerial should be enough to talk to the rig over USB with a modern browser.

Hopefully it should be easy to extend to other modern Yaesu rigs as they share a common CAT interface.

== Design Goals

=== OS and device independence

There is little point in accepting the downsides of doing real-time hardware control in-browser if we need to rely on OS specific hacks or external programs.

=== Keeping transport layer independent

Although WebSerial is a way of getting CAT control accessable to the browser, over-coupling with that transport layer would cause problems when sharing with other apps (virtual serial devices aren't a great solution), and would make it harder to do remote control later.

To start with, I'm going to layer like:

    Serial <----> Message Framer/Deframer <-------> Web Messaging API <----> CAT protocol implementation <-----> UI

and try and keep the messaging layer setup/teardown independent as possible.   The API looks close enough to WebSockets etc that switching it in and out shouldn't be a problem later on.

=== Stateless as possible

The radio is the source of truth for state.

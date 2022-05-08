# digital-loggers-uupy

This started as a port of a python version of the [Digital Loggers UU tool] in order to use it for script commands with [Home Assistant]. In the process I decided to extend it a bit, it has a few new features such as json output and debugging.

NOTE: I only have an [EPCR3]. While I believe this should work with any devices supported by the original UU.pl, use at your own risk. This should not be needed for the latest versions of the Digital Logger products as they have both a Rest API and MMQT, both of which work better with Home Assistant than script commands.

```
Usage: UU <Host>[:port] <login:password> <[n]{on|off|pulse|status|power|name}|runNNN|interact>

Examples:
// Turn outlet 5 on
UU 192.168.0.100:80 admin:1234 5on

// See the status of the outlets
UU 192.168.0.100:80 admin:1234 status

// Turn all outlets on, and outlet 4 off
UU 192.168.0.100:80 admin:1234 on 4off

// See the names of the outlets, the status, turn all on and 4 off, see the status again
UU lpc.digital-loggers.com admin:4321 name status on 4off status

// Run a script starting at line 10, see the outlet names and status
UU lpc.digital-loggers.com admin:4321 run010 name status
```

[Digital Loggers UU tool]: https://www.digital-loggers.com/cex.html
[EPCR3]: https://www.digital-loggers.com/epcr3_faqs.html
[Home Assistant]: https://www.home-assistant.io/

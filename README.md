# airprom - lightweight prometheus collector for Philips Air Purifiers

This is a simple Prometheus metrics collection bridge for Philips' Wi-Fi connected air purifiers.
It is based upon [py-air-control](https://github.com/rgerganov/py-air-control/), and Flask

Only CoAP purifiers are supported, and it is only tested with the AC2889/10. I made this as a 
quick hack for my own use. Status requests are sent to the purifier in response to Prometheus
scrapes

Start it with the IP or hostname of your purifier and any required parameters, e.g.

```
$ airprom --listen "::0" 192.168.1.33
```


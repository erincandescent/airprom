#!/usr/bin/env python3
import argparse

from flask import Flask
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import prometheus_client as prom
from pyairctrl.coap_client import CoAPAirClient
from prometheus_client.core import InfoMetricFamily, GaugeMetricFamily, REGISTRY

app = Flask(__name__)

@app.route("/")
def index():
	return "You maybe want /metrics"

# Pass /metrics to prometheus
app_dispatch = DispatcherMiddleware(app, {
	'/metrics': prom.make_wsgi_app()
})


# Collect the metrics pewpewpew
class CustomCollector(object):
	def __init__(self, ip):
		self.ip = ip

	def collect(self, describing=False):
		if not describing: 
			cli = CoAPAirClient(self.ip)
			status = cli.get_status()

			if "name" not in status:
				return
			labels = [self.ip, status["name"]]

		label_names = ["device_hostname", "name"]

		device_info = InfoMetricFamily('air_purifier_device_info', 'Air Purifier Device Information', labels=label_names)
		if not describing:
			device_info.add_metric(labels, {
				"type": status["type"],
				"mode": status["mode"],
				"model": status["modelid"],
				"software_version": status["swversion"],
				"wifi_version": status["WifiVersion"],
				"product_id": status["ProductId"],
				"device_id": status["DeviceId"],
				"status_type": status["StatusType"],
				"connect_type": status["ConnectType"],
			})
		yield device_info

		def gauge(name, desc, field_name, xfrm=lambda x: x):
			if not describing and field_name not in status:
				return None
			g = GaugeMetricFamily("air_purifier_" + name, "Air Purifiier " + desc, labels=label_names)
			if not describing:
				g.add_metric(labels, xfrm(status[field_name]))
			yield g

		yield from gauge("runtime", "running time", "runtime", lambda x: x/1000)
		yield from gauge("on", "powered on", "pwr")

		def fan_speed_xfrm(om):
			if om == "s":
				fan_speed = 0
			elif om == "t":
				fan_speed = 9
			else:
				fan_speed = int(om)
			return fan_speed
		yield from gauge("fan_speed", "fan speed setting", "om", fan_speed_xfrm)
		yield from gauge("pm25", "PM 2.5 level ug/m3","pm25")
		yield from gauge("iaql", "Indoor Air Quality Index", "iaql")
		yield from gauge("pre_filter_time_til_clean", "Pre filter hours remaining", "fltsts0")
		yield from gauge("hepa_filter_time_til_replace", "Pre filter hours remaining", "fltsts1")
		yield from gauge("carbon_filter_time_til_replace", "Carbon filter hours remaining", "fltsts2")

	def describe(self):
		return self.collect(describing=True)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('ip', metavar='c', type=str, nargs=1,
					help='Device IP or hostname')
	parser.add_argument("--listen", default="localhost", help="Listen on IP/hostname", type=str)
	parser.add_argument("--port", default=5000, help="Listen on port", type=int)
	parser.add_argument("--debug", help="Enable debug features", action='store_const', default=False, const=True)
	args = parser.parse_args()

	REGISTRY.register(CustomCollector(args.ip[0]))

	run_simple(args.listen, args.port, app_dispatch, use_reloader=args.debug, use_debugger=args.debug, use_evalex=args.debug)

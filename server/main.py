from flask import Flask, request, abort
app = Flask(__name__)
import logging
import syslog_client

LOG_LEVEL = 'DEBUG'
SYSLOG_HOST = 'localhost'


def init_logger():
    global LOG_LEVEL
    log = logging.getLogger('infra-monitor-server')
    log.setLevel(LOG_LEVEL)
    log.propagate = False
    stderr_logs = logging.StreamHandler()
    stderr_logs.setLevel(getattr(logging, LOG_LEVEL))
    stderr_logs.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(stderr_logs)
    return log

def write_to_syslog(payload):
    sclient.warn(payload)


def handle_alert(alert_struct):
    check_name = alert_struct['name']
    description = alert_struct['description']
    host = alert_struct['host']
    message = "Rancher Infrastructure Event Alarm - " \
              "The following check has failed on host {host}: {check_name}. Check Description: {check_desc}".format(
        host=host,
        check_name=check_name,
        check_desc=description
    )
    log.debug("Sending the following to syslog {0}".format(message))
    write_to_syslog(message)


@app.route("/report_alert", methods=['POST'])
def report_alert():
    '''
    report monitoring alert
    :return:
    '''
    if not request.json:
        log.error('received non-json data')
        abort(400)

    log.debug(request.json)
    handle_alert(request.json)
    return 'OK'


if __name__ == "__main__":
    log = init_logger()
    sclient = syslog_client.Syslog(host=SYSLOG_HOST)
    log.info('Starting server')
    app.run(host="0.0.0.0", port=5050, debug=False)
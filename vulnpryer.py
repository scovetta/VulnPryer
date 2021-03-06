#!/usr/bin/env python

import argparse
from datetime import date, timedelta
from dateutil.parser import parse
# from time import ctime
import logging
import sys

# VulnDB components
from vulndb import query_vulndb
from shiploader import load_mongo, get_extract
from forklift import get_trl, modify_trl, post_trl

# set default dates
to_date = date.today()
from_date = to_date + timedelta(days=-1)


def mkdate(datestr):
    """Coerce arguments into date type"""
    if not isinstance(datestr, date):
        return parse(datestr)
    else:
        return datestr

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--enddate', type=mkdate, default=to_date,
                    help="Start date.")
parser.add_argument('-s', '--startdate', type=mkdate, default=from_date,
                    help="End date.")
parser.add_argument('-l', '--loglevel', default="info", help="Log level.")
args = parser.parse_args()

start_string = args.startdate
start_string = start_string.strftime("%Y-%m-%d")
end_string = args.enddate
end_string = end_string.strftime("%Y-%m-%d")

# set logging level
numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level; %s' % args.loglevel)
logging.basicConfig(stream=sys.stdout,
                    level=numeric_level,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('vulnpryer')
logger.info("Range requested {} - {}".format(start_string, end_string))
print("Range requested {} - {}".format(start_string, end_string))
query_vulndb(args.startdate, args.enddate)

logger.info("Loading data into Mongo.")
print("Loading data into Mongo.")
load_mongo('data_*.json')

logger.info("Generating extract.")
print("Generating extract.")
get_extract('/tmp/vulndb_export.csv')

logger.info("Fetching RedSeal TRL.")
print("Fetching RedSeal TRL.")
get_trl('/tmp/trl.gz')

logger.info("Generating modified TRL.")
print("Generating modified TRL.")
new_trl_path = modify_trl('/tmp/trl.gz')

logger.info("Posting modified TRL to S3.")
print("Posting modified TRL to S3.")
post_trl(new_trl_path)

logger.info("VulnPryer run complete.")
print("VulnPryer run complete.")

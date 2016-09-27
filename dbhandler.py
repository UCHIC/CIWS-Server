from pymongo import MongoClient

#Open connection to db
current_db = MongoClient('localhost').ciwsdb

#Access a collection within db
campusrec = current_db.campusrec

def waterusagedb(buildingid, water_usage_inst):
	#function to write water_usage_inst to db.collection
	waterusagerecord = {}
	campusrec.insert(waterusagerecord)

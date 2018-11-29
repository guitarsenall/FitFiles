
# search_records.py

# crack the record.type
from datetime import datetime
from fitparse import Activity
FileLoc = r'S:\\will\\documents\\OneDrive\\bike\\activities\\will\\'
#fitfilepath = FileLoc + r'2018-06-01-11-13-49.fit'  # long ride
fitfilepath = FileLoc + r'2016-07-09-13-52-59.fit'  # problems
activity = Activity(fitfilepath)
activity.parse()
records = activity.records
record_types = set()
for record in records:
    record_types.add(record.type.name)
fields_by_type  = {}
for RType in record_types:
    print 'type = %s' % RType
    records = activity.get_records_by_type(RType)
    RecNum  = 0
    fields_by_type[RType] = set()
    for record in records:
        valid_field_names = record.get_valid_field_names()
        #print '    name = ',
        for name in valid_field_names:
            fields_by_type[RType].add(name)
#            print name + ', ',
#            if 'balance' in name.lower():
#                print 'balance found in %s field within %s record type' \
#                        % (name, RType)
#        if RType == 'record':
#            print '*',
#        else:
#            print '.',
        RecNum  += 1
    fields_by_type[RType].add('number of records: %s' % RecNum)
    print '.'

for RType in fields_by_type.keys():
    print 'record type: %s' % RType
    for field in fields_by_type[RType]:
        print '    ' + field

# get session info
print 'session record fields:'
records = activity.get_records_by_type('session')
for record in records:
    valid_field_names = record.get_valid_field_names()
    for name in valid_field_names:
        print '   ' + name + ': ', record.get_data(name), ' ', \
            record.get_units(name)

#for record in records:
#    print record.type.name
#    print record.get_valid_field_names()
#    break




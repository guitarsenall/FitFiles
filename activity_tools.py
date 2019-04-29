
#   activity_tools.py

class UnitHandler():
    '''
    class for converting units on signals (a dictionary defined below
    in extract_activity_signals).
    Define converter functions first so they can be stored in the
    UnitConverters dictionary upon initialization.
    '''

    def from_degF_to_degC(self, degF):
        return (degF-32.0)*5.0/9.0
    def from_degC_to_degF(self, degC):
        return 9.0/5.0*degC + 32.0
    def from_mps_to_mph(self, speed):
        return 2.23694*speed
    def from_m_to_feet(self, distance):
        return 3.28084*distance
    def from_m_to_miles(self, distance):
        return 0.000621371*distance

    def __init__(self, UserUnits):
        '''
        Initialize with a set of UserUnits--a dictionary whose keys are the
        names of channels to convert and whose values are the preferred units
        to convert to.
        '''
        self.UserUnits = UserUnits
        # assemble the UnitConverters dictionary.
        self.UnitConverters = {}
        # The first key is the From-Unit--a unit to convert from.
        # and the second key is the To-Unit--the preferred unit.
        #                   From    To
        self.UnitConverters['C'  ] = {}
        self.UnitConverters['C'  ]['F'   ]  = self.from_degC_to_degF
        self.UnitConverters['m/s'] = {}
        self.UnitConverters['m/s']['mph' ]  = self.from_mps_to_mph
        self.UnitConverters['m'  ] = {}
        self.UnitConverters['m'  ]['feet']  = self.from_m_to_feet
        self.UnitConverters['m'  ]['miles'] = self.from_m_to_miles

    def ConvertSignalUnits(self, signals):
        ChannelList = signals.keys()
        ChannelList.remove('time')
        ChannelList.remove('metadata')
        for channel in ChannelList:
            FromUnit    = signals['metadata']['units'][channel]
            if self.UserUnits.has_key(channel):
                ToUnit  = self.UserUnits[channel]
                if self.UnitConverters.has_key(FromUnit):
                    if self.UnitConverters[FromUnit].has_key(ToUnit):
                        converter   = self.UnitConverters[FromUnit][ToUnit]
                        signals['metadata']['units'][channel] = ToUnit
                        signals[channel] = converter(signals[channel])
        return signals

def extract_activity_laps(activity):
    '''
    Function to extract lap results from activity object
    '''
    from fitparse import Activity

    activity.parse()
    records = activity.get_records_by_type('lap')
    current_record_number = 0

    elapsed_time    = []
    timer_time      = []
    avg_heart_rate  = []
    avg_power       = []
    avg_cadence     = []
    max_heart_rate  = []
    balance         = []
    lap_timestamp   = []
    lap_start_time  = []

    FirstIter   = True

    for record in records:

        # Print record number
        current_record_number += 1
        #print >> OutStream, (" Record #%d " % current_record_number).center(40, '-')

        # Get the list of valid fields on this record
        valid_field_names = record.get_valid_field_names()

        for field_name in valid_field_names:
            # Get the data and units for the field
            field_data = record.get_data(field_name)
            field_units = record.get_units(field_name)

            ## Print what we've got!
            #if field_units:
            #    print >> OutStream, " * %s: %s %s" % (field_name, field_data, field_units)
            #else:
            #    print >> OutStream, " * %s: %s" % (field_name, field_data)

            if 'timestamp' in field_name:
                lap_timestamp.append( field_data )
                if FirstIter:
                    t0  = field_data    # datetime
                    t   = t0
                    FirstIter   = False
                else:
                    t   = field_data    # datetime

            if 'start_time' in field_name:
                lap_start_time.append( field_data )

            if 'total_elapsed_time' in field_name:
                elapsed_time.append( field_data )

            if 'total_timer_time' in field_name:
                timer_time.append( field_data )

            if 'avg_power' in field_name:
                avg_power.append( field_data )

            # avg_heart_rate is in a lap record
            if 'avg_heart_rate' in field_name:
                avg_heart_rate.append(field_data)

            if 'max_heart_rate' in field_name:
                max_heart_rate.append(field_data)

            if 'avg_cadence' in field_name:
                avg_cadence.append(field_data)

            if 'left_right_balance' in field_name:
                balance.append(field_data)

    #from numpy import nonzero, array, arange, zeros, average, logical_and
    import numpy as np

    laps    = {}
    laps['total_elapsed_time']  = np.array(elapsed_time)
    laps['total_timer_time']    = np.array(timer_time)
    laps['avg_hr']              = np.array(avg_heart_rate)
    laps['power']               = np.array(avg_power)
    laps['cadence']             = np.array(avg_cadence)
    laps['time']                = np.array(elapsed_time)
    laps['max_hr']              = np.array(max_heart_rate)
    if len(balance) == 0:
        laps['balance']         = np.zeros(len(avg_power))
    else:
        laps['balance']         = np.array(balance)
    laps['start_time']          = np.array(lap_start_time)
    laps['timestamp']           = np.array(lap_timestamp)

    return laps

# end extract_activity_laps()

def extract_activity_signals(activity, resample='constant', verbose=False):
    '''
    function to extract constant-increment signals from
    activity object.
    resample keyword:
        'constant' results in constant-increment time data
        'existing' results in variable-increment time data at measured samples
        default yields the data lists.
    '''

    from datetime import datetime
    from fitparse import Activity

    activity.parse()
    records = activity.get_records_by_type('record')
    current_record_number = 0

    data_signals                        = {}
    data_signals['metadata']            = {}
    data_signals['metadata']['units']   = {}
    data_lists          = {}        # empty dictionary for lists
    nonnumeric_lists    = {}
    time_values         = set()     # all existing time values
    time_stamps         = set()     # all existing time values
    FirstIter           = True

    for record in records:

        # Print record number
        current_record_number += 1
        if verbose:
            print (" Record #%d " % current_record_number).center(40, '-')

        # Get the list of valid fields on this record
        valid_field_names = record.get_valid_field_names()

        # get the timestamp. Should be present.
        if 'timestamp' not in valid_field_names:
            raise AssertionError('timestamp not found in record ' \
                        + str(current_record_number) )
        field_data  = record.get_data('timestamp')    # datetime
        if FirstIter:
            t0  = field_data    # datetime
            t   = t0
            FirstIter   = False
        else:
            t   = field_data    # datetime
        time_stamps.add( t )
        dt  = t-t0
        time_values.add( dt.total_seconds() )
        valid_field_names.remove('timestamp')

        for field_name in valid_field_names:
            # Get the data and units for the field
            field_data  = record.get_data(field_name)
            field_units = record.get_units(field_name)

            # ignore possible unit discrepancy between samples
            data_signals['metadata']['units'][field_name] = field_units

            # ignore non-numeric data fields
            if isinstance(field_data, (int, long, float)):
                if field_name not in data_lists.keys():
                    data_lists[field_name] = [ (dt.total_seconds(), \
                                                field_data)         ]
                else:
                    data_lists[field_name].append( (dt.total_seconds(), \
                                                    field_data)         )
            else:
                if field_name not in nonnumeric_lists.keys():
                    nonnumeric_lists[field_name] = [ (dt.total_seconds(), \
                                                field_data)         ]
                else:
                    nonnumeric_lists[field_name].append( (dt.total_seconds(), \
                                                    field_data)         )

    if verbose:
        print 'finished extracting lists'

    if verbose:
        for field in data_lists.keys():
            print field + ': ' + str( len(data_lists[field]) ) + ' points'
    #                    distance: 3635 points
    #                    temperature: 3635 points
    #                    power: 3631 points
    #                    heart_rate: 3635 points
    #                    altitude: 3635 points
    #                    position_long: 3635 points
    #                    position_lat: 3635 points
    #                    speed: 3635 points
    #                    cadence: 3629 points

    #
    #   Resample to constant increment
    #
    import numpy as np  # or pylab

    if resample == 'constant':
        nPts            = long( dt.total_seconds() + 1 )
        const_time      = np.arange(nPts).astype(float)  # sample interval of 1 sec
        data_signals['metadata']['timestamp']   = t0
        data_signals['time']    = const_time
        for field in data_lists.keys():
            var_matrix  = np.transpose(np.array( data_lists[field] ))
            var_t       = var_matrix[0,:]
            var_s       = var_matrix[1,:]
            # resample. lists get converted to arrays on input.
            const_sig   = np.interp(const_time, var_t, var_s)
            data_signals[field] = const_sig
        return data_signals
    elif resample == 'existing':
        # interpolate values at all existing time points
        time_vector     = np.array(list(time_values)).astype(float)
        data_signals['metadata']['timestamp']   = t0
        data_signals['time']    = time_vector
        for field in data_lists.keys():
            var_matrix  = np.transpose(np.array( data_lists[field] ))
            var_t       = var_matrix[0,:]
            var_s       = var_matrix[1,:]
            # resample. lists get converted to arrays on input.
            new_sig   = np.interp(time_vector, var_t, var_s)
            data_signals[field] = new_sig
        return data_signals
    else:
        return data_lists

# end extract_activity_signals()

def threshold_state_detect( x, OnLevel, OffLevel, DebounceCounts=5 ):
    '''
    detect intervals.
    Return value is a list of dictionaries with keys 'on' and 'off'
    giving samples into x indicating the start and stop indices.
    '''
    from numpy import nonzero, array, arange, zeros

    nPts = len(x)
    OnState = False
    intervals = []
    interval  = {}

    for i in range(0,nPts-DebounceCounts+1):
        OnTestArray = nonzero( x[i:i+DebounceCounts] > OnLevel )[0]
        if len(OnTestArray) == DebounceCounts:
            if not OnState:
                # new interval begins
                print 'interval detected at sample %i' % i
                interval['on'] = i
            OnState = True
        OffTestArray = nonzero( x[i:i+DebounceCounts] < OffLevel)[0]
        if len(OffTestArray) == DebounceCounts:
            #print 'OnState set to False at sample %i' % i
            if OnState:
                # interval ends
                print 'interval ended at sample %i' % i
                interval['off'] = i
                intervals.append( interval.copy() )
            OnState = False

    return intervals

# end threshold_state_detect()

def running_minimum( x, boxcar=8 ):
    '''
    Like it says, a running minimum over the given boxcar length
    '''
    from numpy import zeros
    nPts = len(x)
    run_min = zeros(nPts)
    for i in range(boxcar-1,nPts):
        iBeg = 0 if i<boxcar-1 else i-boxcar+1
        iEnd = i    # placeholder
        run_min[i] = min( x[iBeg:iEnd] )
    return run_min
# end running_minimum()

def find_delay(a, b, MinDelay=0, MaxDelay=20):
    '''
    find the delay in a relative to b
    (a positive delay means a looks like a delayed version of b)
    '''
    from numpy import zeros, sqrt, average
    FirstIter   = True
    for i in range(MinDelay, MaxDelay+1):
        if i==0:
            c = b - a
        elif i>0:
            c = b[0:-i] - a[i:]
        else:
            c = b[-i:] - a[0:i]
        rms = sqrt(average( c**2 ))
        #print '    delay: %i, rms = %6.3f' % (i,rms)
        if FirstIter:
            MinRMS  = rms
            iMin    = i
            FirstIter   = False
        else:
            if rms < MinRMS:
                MinRMS  = rms
                iMin    = i
    #print '  minimum RMS is ', MinRMS
    #print '  delay with minimum RMS is ', iMin
    return iMin
# end find_delay()


def new_find_delay( A, B, MinRMSLength=10 ):
    '''
    find the delay in A relative to B
    (a positive delay means A looks like a delayed version of B)
    For derivation, see analysis_notes.txt.
    MinRMSLength is the minimum number of samples in the
    RMS vector, C. This should be enough samples to avoid the
    possibility of getting unlucky with a low RMS with few samples.
    '''
    from numpy import zeros, sqrt, average
    nA  = len(A)
    nB  = len(B)
    FirstIter   = True
    iBeg    = MinRMSLength
    iEnd    = nA+nB-1 - MinRMSLength
    for i in range( iBeg, iEnd ):
        d   = i - nB + 1    # delay associated with i
        if i < nB:
            Abeg = 0
            Bbeg = nB-1-i
        else:
            Abeg = i-nB+1
            Bbeg = 0
        if i < nA-1:
            Aend = i+1
            Bend = nB
        else:
            Aend = nA
            Bend = nB-(i-nA)-1
        C = B[Bbeg:Bend] - A[Abeg:Aend]
        rms = sqrt(average( C**2 ))
        #print '    delay: %i, rms = %6.3f' % (i,rms)
        if FirstIter:
            MinRMS      = rms
            BestIndex   = i
            BestDelay   = d
            FirstIter   = False
        else:
            if rms < MinRMS:
                MinRMS  = rms
                BestIndex   = i
                BestDelay   = d
    print 'minimum RMS is ', MinRMS
    print 'delay with minimum RMS is %i at i == %i' % (BestDelay,BestIndex)
    return (BestDelay,BestIndex)
# end find_delay()


import os

def FindConfigFile(CodePath, FilePath):
    # attempt to find appropriate config file
    # add os.getcwd() to search path, prioritize CodePath.
    search_paths   = [ CodePath, os.getcwd(), FilePath ]
    if 'kim' in FilePath.split('\\')[-1]:
        ConfigFileName = r'\cyclingconfig_kim.txt'
    else:
        ConfigFileName = r'\cyclingconfig_will.txt'
    for SearchPath in search_paths:
        if os.path.exists(SearchPath + '\\' + ConfigFileName):
            return SearchPath + '\\' + ConfigFileName
    return None


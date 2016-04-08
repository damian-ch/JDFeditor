import jdf_lib

my_data_variable = jdf_lib.load_database('sample_data.jdf')
if my_data_variable == -1:
    print 'load error'
else:
    print my_data_variable[0]
    print my_data_variable[1]
    print my_data_variable[2]
    my_database = my_data_variable[2]
    print my_database[2][1]
raw_input('press enter')

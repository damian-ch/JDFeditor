##Quick set-up

I sincerely apologise for the lack of information in here. Will expand on it soon.

Step 1. Enter data into the database.
Step 2. In your python code import jdf_lib and use the built-in function load_database()
Step 3. Something else


Run the code below to see how the jdf_lib works.
Make sure to have jdf_lib.py and sample_data.jdf in the same folder,
for the example to work.

###Sample code
####you can find this code in the JDFeditor/sample_data/sample_code.py


~~~~Python
import jdf_lib

my_data_variable = jdf_lib.load_database('sample_data.jdf')
if my_data_variable == -1:
    print 'load error'
else:
    print my_data_variable[0]
    print my_data_variable[1]
    print my_data_variable[2]
raw_input('press enter')
~~~~

###Explanation

jdf_lib.load_database() function takes one argument: the file name or the file path.
If the file is successfully loaded the data will be returned. In the above example
the returned data is placed in my_data_variable.

Index 0 of `my_data_variable` holds the types of columns in the database.
Index 1 of `my_data_variable` holds the names of columns in the database.
Index 2 of `my_data_variable` holds the actual values of the database.
-> Therefore, every index of `my_data_variable[2]` is an every row of the database.
 ---> Consequently, every index of `my_data_variable[2][row]` is an every column of the database.

If you are concerned by the content of the database only, a good practice is
to make a variable that holds the information of the third index:

    my_database = my_data_variable[2]

the following would print then the value of row 2 and column 1:

    print my_database[2][1]

Which in the case of sample_data.jdf is the value: 1460
Remember that indexing starts at 0, not 1.

Some addition at the end of the file

# CMPUT 291 MINI PROJECT 1 ASSIGNMENT (FALL 2015- SEC A1)
# ALAN ZHANG, CCID 1295834, LAB D06
# IMRAN ALI, CCID 1447593, LAB D02

import sys
import cx_Oracle # to access oracle in python
import getpass # getting password from user without displaying it
import random # to generate a random ticket number
import string # in order to get string/ascii letters for the random ticket

def interface():
    
    username = input("Username: ")
    
    if not username:
        username = getpass.getuser()
    
    # obtaining the password    
    password = getpass.getpass()
    
    # contatenating the strings to get an address to be tested in connection
    
    connect_string = ''+username+'/' + password + '@gwynne.cs.ualberta.ca:1521/CRS'
    

            
    try:
        # attempt the connection to Oracle and intitiating the cursor
        connection = cx_Oracle.connect(connect_string)
        curs = connection.cursor()             
                  i= True
        start = True
        air_start = False
        while i:
            print() # printing a new line 
            user_input = input("Registered or Unregistered User or exit? (r/u/exit): ")
        
        # the input from user is lower cased for error handling
            user_input = user_input.lower()
        
        # if the input from user is an empty string, such as when the pressed enter, go back to original while loop
            if user_input == '':
                print("Invalid input")
            elif (str(user_input) == 'r') or (str(user_input) == 'u'):
                user_email = input("Enter email: ")
                
                if user_email == '':
                    print("Invalid input")
                elif len(str(user_email)) > 20: # if the length of user inputted email is greater than 20, the individual violated the table constraint of 20 chars
                    print("Email is too long")
                elif str(user_input) == "u": # if user is unregistered, they are prompted to create a new user_email and password to be placed into the users table
                    user_email = str(user_email)
                    password = input("Enter password (4 characters): ")
                    
                    if len(str(password)) != 4: # invalid length of the individual inputted a password length that is not a length of 4 
                        print("Invalid password, has to be length of 4")
                    else:
                        # if all executes, user id is created and the system date is inserted into the users table under last_login
                        print("User ID is created. please log in as a registered user")
                        curs.execute("select SYSDATE from dual")
                        date = curs.fetchall()
                        user_data = [(user_email),(password),(date[0][0])]
                        curs.bindarraysize = 1
                        curs.setinputsizes(20,4, cx_Oracle.Date)
                        curs.execute("insert into users(email,pass,last_login)""values(:1,:2,:3)",(user_data))
                        connection.commit()
                        i = False
                else:
                    # if the user is a registered user, the individual is asked to input the password to fetch the data
                    user_email = str(user_email)
                    password = input("Enter password (4 characters): ")
                    
                    if len(str(password)) != 4:
                        print("Invalid password, has to be length of 4")
                    else:
                        curs.execute("Select * from users")
                        rows = curs.fetchall()
                        # this makes sure that the user_email is within the length of 20 and if so, a space is padded within the values 
                        while len(user_email) < 20:
                            user_email = user_email + " "
                        registered = False
                        # if the executed query is equivalent to the password that the individual wrote, the individual is registered. Else they have to register 
                        for row in rows:
                            if (user_email == row[0]) and (password == row[1]):
                                registered = True
                        if not registered:
                            print("Sorry you aren't registered")
                        else:
                            print("Welcome back")
                            i = False
            # from the menu, if the individual chooses to type in exit, the connection and cursor are closed and nothing is updated, anything else is invalid
            elif str(user_input) == 'exit':
                curs.close()
                connection.close()
                i = False
                start = False
            else:
                print("Invalid input")
        curs.execute("select email from airline_agents")
        air_agents = curs.fetchall()
        for agents in air_agents:
            if user_email == agents[0]:
                start = False
                air_start = True
        while air_start:
            print() # to print a new line
            selection = input('''Specify what you would like to do
1. Search for flights, 
2. List existing booking(s),
3. Record a flight departure
4. Record a flight arrival
5. Logout 
-------------------------------
''')
            # if the selection is 1, search function is initiated, if it is 2, existing bookings function is initiated, and if 3, the individual has the option to log out
            selection = str(selection)
            
            if selection == "1":
                search(curs,user_email,connection)
            elif selection == "2":
                existingBookings(user_email, curs,connection)
            elif selection == "3":
                not_recorded = True
                while not_recorded:
                    # this functions to change the actual departure time if the individual is an airline agent
                    flight_dep = input('''Please enter the flight number of the that flight that you want to update (q to quit): ''')
                    flight_dep = str(flight_dep)
                    curs.execute("select act_dep_time from sch_flights where flightno = '" + flight_dep.upper() + "'")
                    departed =  curs.fetchall()
                    if flight_dep == '':
                        print("Invalid input")
                    elif flight_dep.upper() == "Q":
                        print("returning to main menu")
                        not_recorded = False
                    elif departed == []:
                        print("Sorry that's not a valid flight number try again")
                    else:
                        # this makes sure the departure time is inputted correctly, prior to changing it
                        while True:
                            new_time = input("Please enter the departure time of the flight in the format (HH24:MI) (q to quit) : ")
                            new_time = str(new_time)
                            if new_time == '':
                                print("Invalid input")
                            elif new_time.upper() == "Q":
                                print("Returning to flight selection")
                                break
                            # if the length of the time in the format is not 00:00, then the time is invalid
                            elif len(new_time) != 5:
                                print("Invalid length use the format please")
                                # if the first two inputs ie. 12:XX are not digits, it will return False therefore prompting to fix it
                            elif (new_time[0] + new_time[1]).isdigit() ==  False:
                                print("Please use the format")
                                # if the last two inputs ie. XX:12 are not digits, it will return False therefore prompting to fix it
                            elif (new_time[3] + new_time[4]).isdigit() == False:
                                print("Please use the format")
                                # error handling where the middle is ":" and if the XX:_X is less than 6 and if the first two numbers inputted is less than 24 hours, update the departure time
                            elif new_time[2] == ":" and new_time[3] < "6" and (int(new_time[0] + new_time[1]) < 24):
                                curs.execute("update sch_flights set act_dep_time = to_date('" + new_time + "', 'HH24:MI') where flightno = '" + flight_dep.upper() + "'")
                                connection.commit()
                                print("You have updated flight " + flight_dep.upper() + " with the new time of " + new_time)
                                not_recorded = False
                                break
                            else:
                                print("Incorrect format for the time. Try again")
                                
            elif selection == "4":
                not_recorded = True
                while not_recorded:
                    # this does the same as above but with arrival time for airline agents
                    flight_arr = input('''Please enter the flight number of the that flight that you want to update (q to quit): ''')
                    flight_arr = str(flight_arr)
                    curs.execute("select act_arr_time from sch_flights where flightno = '" + flight_arr.upper() + "'")
                    arrived =  curs.fetchall()
                    
                    if flight_arr == '':
                        print("Invalid input")
                    elif flight_arr.upper() == "Q":
                        print("Returning to menu")
                        not_recorded = False             
                    elif arrived == []:
                        print("Sorry that's not a valid flight number try again")
                    else:
                        while True:
                            new_time = input("Please enter the arrival time of the flight in the format (HH24:MI) (q to quit) : ")
                            new_time = str(new_time)
                            if new_time == '':
                                print("Invalid input")
                            elif new_time.upper() == "Q":
                                print("Returning to flight selection")
                                break
                            elif len(new_time) != 5:
                                print("Invalid length use the format please")
                            elif (new_time[0] + new_time[1]).isdigit() ==  False:
                                print("Please use the format")
                            elif (new_time[3] + new_time[4]).isdigit() == False:
                                print("Please use the format")
                            elif new_time[2] == ":" and new_time[3] < "6" and (int(new_time[0] + new_time[1]) < 24):
                                curs.execute("update sch_flights set act_arr_time = to_date('" + new_time + "', 'HH24:MI') where flightno = '" + flight_arr.upper() + "'")
                                connection.commit()
                                print("You have updated flight " + flight_arr.upper() + " with the new time of " + new_time)
                                not_recorded = False
                                break
                            else:
                                print("Incorrect format for the time. Try again")
            elif selection == "5":
                log_me_out = input("Are you sure you want to logout (y/n): ")
                log_me_out = str(log_me_out)
                log_me_out = log_me_out.lower() # input is lowercased so they can type YES or Y and program can still go through
                if (str(log_me_out) == 'yes') or (str(log_me_out) == 'y'):
                    
                    # take the system date and update the last_login for the user with that email
                    curs.execute("select to_char(SYSDATE,'DD-Mon-YYYY') from dual")
                    date1 = curs.fetchall()
                    curs.execute("UPDATE USERS set last_login = '" + str(date1[0][0]) + "' where email = '"+ str(user_email) +"'")
                    connection.commit() # inserting, deleting, updating requires a commit() statement
                    i = True
                    start = False # 
                    air_start = False
                else:
                    start = True
            else:
                print("Invalid input")
        
        
        while start:
            print() # to print a new line
            selection = input('''Specify what you would like to do
1. Search for flights, 
2. List existing booking(s), 
3. Logout: 
-------------------------------
''')
            # if the selection is 1, search function is initiated, if it is 2, existing bookings function is initiated, and if 3, the individual has the option to log out
            selection = str(selection)
            
            if selection == "1":
                search(curs,user_email,connection)
            elif selection == "2":
                existingBookings(user_email, curs,connection)
            elif selection == "3":   
                log_me_out = input("Are you sure you want to logout (y/n): ")
                log_me_out = str(log_me_out)
                log_me_out = log_me_out.lower() # input is lowercased so they can type YES or Y and program can still go through
                if (str(log_me_out) == 'yes') or (str(log_me_out) == 'y'):
                    
                    # take the system date and update the last_login for the user with that email
                    curs.execute("select to_char(SYSDATE,'DD-Mon-YYYY') from dual")
                    date1 = curs.fetchall()
                    curs.execute("UPDATE USERS set last_login = '" + str(date1[0][0]) + "' where email = '"+ str(user_email) +"'")
                    connection.commit() # inserting, deleting, updating requires a commit() statement
                    i = True
                    start = False # to break out of the while loop
                else:
                    start = True
            else:
                print("Invalid input")
        if i: # to close the loop and connection altogether
            curs.close()
            connection.close()
        
    except cx_Oracle.DatabaseError as exc: # if any oracle errors arises due to executing sql statements ie. invalid variables, inserting null characters
        error, = exc.args
        print( sys.stderr, "Oracle code:", error.code)
        print( sys.stderr, "Oracle message:", error.message)
            
def search(curs,email,connection):      
    try: 
        # if the views exists, they are dropped for the views to be remade in this function 
        curs.execute("drop view available_flights")
        curs.execute("drop view good_connections")      
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print()
    
    validS = True
    while validS:
        source_search = input("Provide a source airport: ")                     
    
        if source_search == '':
            print("Invalid input")
        else: 
            # to execute a query to obtain the acode if the individual inputted it correctly ie. YEG, LAX
            query1 = "select acode from airports where acode ='" + str(source_search.upper()) + "'"
            curs.execute(query1)
            rows = curs.fetchall()
            # to concatenate the string of source search such that the first letter is capitalized and the letters later on are not (ie. Edmonton, Calgary)
            source_searchC = str(source_search[0].upper()) + str(source_search[1:].lower())
            if rows != []:
                source = rows[0][0]
            else:
                source = rows
            if rows == []: # use of partial matching if the name given is similar to the actual airport name from the table, this returns the acode from airports
                query1 = "select distinct acode from airports where name like " + "'%" + str(source_search) + "%' or name like '%"+ str(source_searchC) + "%'"
                curs.execute(query1)
                row1 = curs.fetchall()
                selection = []
                counter = 0
                # if it exists, the acode is placed inside selection container
                if len(row1) > 0:
                    for acode in row1:
                        print(acode[0])
                        selection.append(acode[0])
                    selectS = input("Enter the airport code you would like to select: ")
                    if selectS.upper() in selection:
                        for codes in selection:
                            if selectS.upper() == codes:
                                source = codes
                            else:
                                counter += 1
                if row1 == []: # use of partial matching if the city given is similar to the actual city name from the table, this returns the acode from airports
                    query1 = "select distinct acode from airports where city like '%" + source_search + "%' or city like '%" + source_searchC + "%'"
                    curs.execute(query1)
                    row2 = curs.fetchall()
                    source = row2
                    selection = []
                    counter = 0
                    # if it exists, the acode is placed inside the selection container
                    if len(row2) > 0:
                        for acode in row2:
                            print(acode[0])
                            selection.append(acode[0])
                        selectS = input("Enter the airport code you would like to select: ")
                        if selectS.upper() in selection:
                            for codes in selection:
                                if selectS.upper() == codes:
                                    source = codes
                                else:
                                    counter += 1             
            if len(source) == 3: # if the source input is actually a viable acode, move onto next step if the individual decides to move onto destination search, else the user tries again until they obtain the proper acode            
                sourceI = input("You have selected the airport with airport code " + str(source) + " is this okay? (y/n): ")
                if sourceI.lower() == "y" or sourceI.lower() == "yes":
                    validS = False
                elif sourceI.lower() == "n" or sourceI.lower() == "no":
                    print("Please try again")
                else:
                    print("Invalid input please try again")
            else:
                print("Invalid input please try again")
        
    validD = True
    while validD:
        # prompt user for a destination airport
        destination_search = input("Provide a destination aiport: ")
        
        if destination_search == '': # if the user entered a blank or pressed enter accidentally
            print("Invalid input")
        else:
            # execute the query with the destination search as the acode
            query2 = "select acode from airports where acode = '" + str(destination_search.upper()) + "'"
        
            curs.execute(query2)
            rowsD = curs.fetchall()
            # capitalize the first letter and the rest of the query
            destination_searchC = str(destination_search[0].upper()) + str(destination_search[1:].lower())
            if rowsD != []:
                destination = rowsD[0][0]
            else:
                destination = rowsD
            if rowsD == []: # use of partial matching if the name of destination airport given is similar to the actual destination name from the table, this returns the acode from airports
                query2 = "select acode from airports where name like '%" + str(destination_search) + "%' or name like '%" + str(destination_searchC) + "%'"
                curs.execute(query2)
                rowsD1 = curs.fetchall()
                selection = []
                counter = 0
                if len(rowsD1) > 0:
                    for acode in rowsD1:
                        print(acode[0])
                        selection.append(acode[0])
                    selectD = input("Enter the airport code you would like to select: ")
                    if selectD.upper() in selection:
                        for codes in selection:
                            if selectD.upper() == codes:
                                destination = codes
                            else:
                                counter += 1                
                if rowsD1 == []: # use of partial matching if the city given for destination is similar to the actual city name from the table, this returns the acode from airports
                    query2 = "select acode from airports where city like '%" + str(destination_search) + "%' or city like '%" + str(destination_searchC) + "%'"
                    curs.execute(query2)
                    rowsD2 = curs.fetchall()
                    selection = []
                    counter = 0
                    if len(rowsD2) > 0:
                        for acode in rowsD2:
                            print(acode[0])
                            selection.append(acode[0])
                            # place into the selection container, and enter which acode they would like to select 
                        selectD = input("Enter the airport code you would like to select: ")
                        if selectD.upper() in selection:
                            for codes in selection:
                                if selectD.upper() == codes.upper():
                                    destination = codes
                                else:
                                    counter += 1                    
            if len(destination) == 3: # if the acode typed is the one that they would like to search for, if not they enter a new one
                destinationI = input("You have selected the airport with airport code " + str(destination) + " is this okay? (y/n): ")
                if destinationI.lower() == "y" or destinationI.lower() == "yes":
                    validD = False
                elif destinationI.lower() == "n" or destinationI.lower() == "no":
                    print("Please try again")
                else:
                    print("Invalid input please try again")
            else:
                print("Invalid input please try again")                
    
    validDate = True
    while validDate:
        givenDate = input('''Please specify a departure date(s) in (DD/MM/YYYY) seperate by commas: 
''')
        if givenDate == '':
            print("Invalid input")
        else:
            dateList = givenDate.split(",")
            cFormat = True
            # to check if the date format is correct in the format XX/XX/XXXX 
            for date in dateList:
                if len(date) != 10:
                    print("Please format date " +date+" correctly")
                    cFormat = False
                elif date[2] != "/" or date[5] != "/":
                    print("Please format date " +date+" correctly")
                    cFormat = False
                else:
                    print("You have selected: " + str(date))
            # this is to prompt the user if they got what they wanted, if not try again 
            if cFormat == True:
                validI = input("Is this what you wanted?(y/n): ")
                validI2 = validI.lower()
                if (validI2 == "yes") or (validI2 == 'y'):
                    validDate = False
                elif (validI2 == "no") or (validI2 == 'n'):
                    print("Please try again")
                else:
                    print("Invalid input")
    # query to create the first available flights view, dumped at the beginning of startup, this is made new everytime the function search is called 
    available_flights = "create view available_flights(flightno,dep_date,src,dst,dep_time,arr_time,fare,seats,price) as select f.flightno, sf.dep_date, f.src, f.dst, sf.act_dep_time, sf.act_arr_time, fa.fare, fa.limit-count(tno),fa.price from flights f, flight_fares fa, sch_flights sf, bookings b, airports a1, airports a2 where f.flightno=sf.flightno and f.flightno=fa.flightno and f.src=a1.acode and f.dst=a2.acode and fa.flightno=b.flightno(+) and fa.fare=b.fare(+) and sf.dep_date=b.dep_date(+) group by f.flightno, sf.dep_date, f.src, f.dst, sf.act_dep_time,sf.act_arr_time, fa.fare, fa.limit, fa.price having fa.limit-count(tno) > 0"
    curs.execute(available_flights)
    
    # query to create good connections view using available flights, dumped at the beginning of startup, this is made new everytime the function search is called 
    good_connections = "create view good_connections (src,dst,flightno1,flightno2,price,dep_date,layover, seat1, seat2,arr_time,dep_time)as select a1.src, a2.dst, a1.flightno, a2.flightno, min(a1.price + a2.price),a1.dep_date, a2.dep_time-a1.arr_time,a1.seats, a2.seats,a2.arr_time, a1.dep_time from available_flights a1, available_flights a2 where a1.dst = a2.src and a1.arr_time +1.5/24 <= a2.dep_time and a1.arr_time +5/24 >= a2.dep_time group by a1.src, a2.dst, a2.dep_time ,a1.arr_time, a1.flightno, a2.flightno, a1.seats, a2.seats,a1.dep_date,a2.arr_time, a1.dep_time"
    curs.execute(good_connections);

    validO = True
    while validO:
        print()
        # this is to order by price or number of connections with the view good connections 
        orderBy = input('''Would you like to 
1.Order by price?
2.Order by number of connections? 
---------------------------------
''')
        if orderBy == "1" or orderBy == "2":
            validO = False
        else:
            print("Invalid input try again")
    for dates in dateList: #
        if orderBy == "1":
            flights = "select flightno1, flightno2, src, dst, to_char(dep_time,'HH24:MI'), to_char(arr_time,'HH24:MI'), stops, layover, price, seat1, seat2 from (select flightno1, flightno2, src, dst, dep_time, arr_time, stops,layover, price,seat1,seat2, row_number() over (order by price asc) rn from (select flightno1, flightno2, src, dst, dep_time, arr_time, 1 stops, layover,price,seat1, seat2 from good_connections where to_char(dep_date,'DD/MM/YYYY') = '" + str(dates) + "' and src = '" + str(source) +  "' and dst = '" + str(destination) + "' union select flightno flightno1, '' flightno2,src,dst,dep_time, arr_time,0 stops, 0 layover, price, seats seat1, 0 seat2 from available_flights where to_char(dep_date , 'DD/MM/YYYY') = '" + str(dates) + "' and src = '" + str(source) + "' and dst = '" + str(destination) + "' )) where rn > 0"
        elif orderBy == "2":
            flights = "select flightno1, flightno2, src, dst, to_char(dep_time,'HH24:MI'), to_char(arr_time,'HH24:MI'), stops, layover, price, seat1, seat2 from (select flightno1, flightno2, src, dst, dep_time, arr_time, stops,layover, price,seat1,seat2, row_number() over (order by stops asc) rn from (select flightno1, flightno2, src, dst, dep_time, arr_time, 1 stops, layover,price,seat1, seat2 from good_connections where to_char(dep_date,'DD/MM/YYYY') = '" + str(dates) + "' and src = '" + str(source) +  "' and dst = '" + str(destination) + "' union select flightno flightno1, '' flightno2,src,dst,dep_time, arr_time,0 stops, 0 layover, price, seats seat1, 0 seat2 from available_flights where to_char(dep_date , 'DD/MM/YYYY') = '" + str(dates) + "' and src = '" + str(source) + "' and dst = '" + str(destination) + "' )) where rn > 0"
    
    # this is just to print the table to standard output
        curs.execute(flights)
        rowflights = curs.fetchall()
        print("%7s|" % "Flight1"+"%7s|" %"Flight2"+"%3s|" % "SRC"+"%3s|" %"DST"+"%8s|" % "Dep Time" +"%8s|" % "Arr Time"+"%5s|" % "Stops"+"%7s|" % "Layover"+"%4s|" % "Price"+"%6s|" %"Seats1" +"%6s|"% "Seats2")
        space = 77 * "-"
        print(space)
        for rowf in rowflights:
            print("%-7s|" % rowf[0]+"%-7s|" %rowf[1]+"%-3s|" % rowf[2]+"%-3s|" %rowf[3]+"%-8s|" % rowf[4]+"%-8s|" % rowf[5]+"%-5s|" % rowf[6]+"%-0.6f|" % rowf[7]+"%-4d|" % rowf[8]+"%-6d|" % rowf[9]+"%-6d|"%rowf[10] )
        print()
    # prompt user to do a booking, if not, go back to the main menu    
    booking_activate = input("Do a booking? (y/n): ")
    
    if booking_activate == '':
        print("Invalid input")
    else:
        booking_activate = str(booking_activate)
        booking_activate = booking_activate.lower()
        # if user wants to do a booking, this activates the booking function, if not the main menu is entered 
        if (booking_activate == 'yes') or (booking_activate == 'y'):
            book(email, curs,connection, rowflights, )
        elif (booking_activate == 'no') or (booking_activate == 'n'):
            print("Okay returning to main menu")
        
def book(user_email,curs,connection, allflights): # booking function if the user decides to book from previous booking_activate
    print()
    book_this = True
    while book_this:    
        select_flights = input('''Please select flightno(s)(for connecting flights 
please only enter the first flightno)from the table above and
provide the price (seperate flightno and price by "-", 
seperate each flight by a comma(no space))
------------------------------------------------------------------
''')
        if select_flights == '':
            print("Invalid input")
        else:
            bookingflights = select_flights.split(",")
            for booking in bookingflights:
                if len(booking) > 5:
                    # if the middle is not "-", ie. LLXXX-XXXX (letter is L, X is number)
                    if str(booking[5]) != "-":
                        print("Invalid format please try again")
                    else:
                        book_this = False
                else:
                    print("Invalid format please try again")
                    
    flights = []
    # to split the "-" on that line so from eg. [AC140-100], we get [[AC140,100]] 
    for unbookedflight in bookingflights:
        unbookedflight.strip()
        flights.append(unbookedflight.split("-"))
        
    #this function gets all the flights that the user enters, it checks if they're bookable and books them if they are, and if not it tells them that they did not book it
    booked_flights = []
    for flight in flights:
        didntBook = True
        for bookableflights in allflights:
            name = []
            counter = 0
            for i in bookableflights[0]:
                if counter < 5:
                    name.append(i)
                counter += 1
            newN = "".join(name)
            flight[0] = flight[0].upper()
            if str(flight[0].upper()) == str(newN):
                if int(flight[1]) == int(bookableflights[8]):
                    print("Booking " + str(flight[0]) + " with price " + str(flight[1]))
                    booked_flights.append(bookableflights)
                    didntBook = False
        if didntBook:
            print("Sorry we could not find " + flight[0].upper() + " with price " + flight[1])
    
    # this is to get their information so that we can book a flight their information     
    booking_start = True
    while booking_start:
        obtain_name = input("Enter a name: ")
    
        if obtain_name == '':
            print("Invalid input")
        else:
            obtain_name = str(obtain_name)
            # to capitalize the first letter and concatenate with the rest eg. edmonton will become Edmonton
            obtain_nameC =obtain_name[0].upper() + obtain_name[1:].lower() 
            if len(obtain_nameC) > 20:
                print("Name is too long")
            else:
                # it checks if they're already a passenger if not it will ask them to insert their country and we make them a passenger with that info
                passenger_check = "select p.email, p.name from passengers p where p.email = '" + str(user_email) + "' and p.name = '" + str(obtain_nameC) + "'"
                curs.execute(passenger_check)
                passenger = curs.fetchall()
                if passenger !=  []:
                    print("Welcome back " + obtain_nameC)
                    booking_start = False
                if passenger == []:
                    obtain_country = input('''You are not a passenger at the moment please provide us 
a country to reference you to: ''')
                    if obtain_country == '':
                        print("Invalid input")
                    else:
                        # to capitalize the first letter of the country name and concatenate the rest of the name as it is eg. canada becomes Canada
                        obtain_country = str(obtain_country).lower()
                        obtain_countryC = obtain_country[0].upper() + obtain_country[1:].lower()
                        if len(obtain_countryC) > 10:
                            print("Country name too long")
                        else:
                            # to insert email, name, country to passengers table
                            passenger_data = [(user_email),(obtain_nameC),(obtain_countryC)]
                            curs.bindarraysize = 1
                            curs.setinputsizes(20,20,10)
                            curs.execute("insert into passengers(email,name,country)""values(:1,:2,:3)",(passenger_data))  
                            connection.commit()
                            curs.execute("select * from passengers")
                            rows = curs.fetchall()
                            booking_start = False
    ticket = []
    # this will print the print statement if they didnt book anything
    if booked_flights == []: 
        print("Sorry we couldn't book anything with the data given please try again")
    else:
        for flights in booked_flights:
            # this creates a unique tno
            x = random.randint(0,9) 
            y = random.randint(0,9)
            z = random.randint(0,9)
            random_tno = str(x) + str(y) + str(z)   
            while random_tno in ticket:
                x = random.randint(0,9)
                y = random.randint(0,9)
                z = random.randint(0,9)
                random_tno = str(x) + str(y) + str(z) # this our random ticket number using random module from python
            ticket.append(random_tno)
            # to insert into tickets table with the information tno, name, email
            ticket_data = [int(random_tno),(obtain_nameC),(user_email),float(flights[8])]
            curs.bindarraysize = 1
            curs.setinputsizes(int,20,20,float)            
            curs.execute("insert into tickets(tno,name,email, paid_price)""values(:1,:2,:3,:4)",(ticket_data))
            connection.commit()
            
            # this is to create a seat number eg. 1A, 2E etc.    
            ticket_number = random.randint(1,9)
            ticket_alpha = random.choice(string.ascii_letters)
            random_ticket= str(ticket_number) + str(ticket_alpha)
            # this is to obtain the fare and departure date information with the information given
            if flights[1] != None:
                curs.execute("select fare from flight_fares where flightno = '" + str(flights[0])+ "' and price = " + str(flights[8]/2))
            
                rowfa = curs.fetchall()
                curs.execute("select dep_date from available_flights where flightno = '" +str(flights[0]) + "' and price = " +str(flights[8]/2))
                rowsdep = curs.fetchall()                
            else:
                curs.execute("select fare from flight_fares where flightno = '" + str(flights[0])+ "' and price = " + str(flights[8]))
                rowfa = curs.fetchall()
                
                curs.execute("select dep_date from available_flights where flightno = '" +str(flights[0]) + "' and price = " +str(flights[8]))
                rowsdep = curs.fetchall()                
            
            # insert booking information into bookings table  
            booking_data = [int(random_tno), (flights[0]), rowfa[0][0], rowsdep[0][0],str(random_ticket)]
            curs.bindarraysize = 1
            curs.setinputsizes(int,6,2,cx_Oracle.Date,3)
            curs.execute("insert into bookings(tno,flightno,fare,dep_date,seat)""values(:1,:2,:3,:4,:5)",(booking_data))
            connection.commit()
            print()
            # tells individual that they have successfully booked a flight
            print("You have booked flight "+ flight[0] + " (and the connecting flights if it has any) with ticket number " + str(random_tno))
    
    
def existingBookings(user_email,curs,connection):
    # this to list the existing bookings and prints the information out onto standard output, also contains function to delete an existing booking
    curs.execute("select b.tno, t.name, to_char(b.dep_date,'DD/MM/YYYY'), t.paid_price from bookings b, tickets t where t.tno = b.tno and t.email = '" + str(user_email) + "'")
    printout = curs.fetchall()
    
    # this is used to print the table in a clean format 
    print("%-9s|" % "Ticket No"+"%-20s|" %"Name"+"%-10s|" % "Dep Date"+"%-10s" %"Paid price")
    space = 77 * "-" # just prints out the ------------------
    print(space)
    for row in printout:
        print("%-9s|" % row[0] + "%-20s|" % row[1] + "%-10s|"%row[2] + "%-10s"%row[3])
        
        # this while loop is used to cancel a booking from existing bookings
    validSelection = True
    while validSelection:
        print()
        userSelection = input('''What would you like to do?
1. Cancel a booking
2. View detailed information about a booking
3. Go back to main menu
---------------------------------------------
''')
        # executes the query to obtain the tno from tickets where the user booked a flight with their email and gives the option to remove the booking
        curs.execute("select tno from tickets where email = '" + user_email +"'")
        ticket_numbers = curs.fetchall()        
        if userSelection == '':
            print("Invalid input")
        elif str(userSelection) not in ["1","2","3"]:
            print("Invalid input")
        elif str(userSelection) == "1":
            user_ticket = input("Please specify the ticket number of the booking you would like to remove (q to quit): ")
            if user_ticket.upper() == "Q":
                print("You didn't delete any bookings.")
            else:
                # this is to execute the deletion in the database given the ticket number
                invalidTicket = True
                for tickets in ticket_numbers:
                    if str(user_ticket) == str(tickets[0]):
                        curs.execute("delete from bookings where tno = " + str(tickets[0]))
                        curs.execute("delete from tickets where tno = " + str(tickets[0]))
                        connection.commit()
                        print()
                        print("You have deleted a booking with ticket number "+ str(user_ticket))
                        invalidTicket = False
                if invalidTicket:
                    print("We did not find any tickets that match please try again")
        # this is to view the ticket information including the name, flight number, fare type, seat number, arrival and departure times
        elif str(userSelection) == "2":
            user_ticket = input("Please specify which ticket number you want a closer look at (q to quit): ")
            print()
            if user_ticket.upper() == "Q":
                print("Going back to main menu")
            else:
                invalidTicket = True
                for ticket in ticket_numbers:
                    if str(ticket[0]) == str(user_ticket):
                        curs.execute("select t.name, b.flightno, b.fare, b.seat, to_char(b.dep_date,'DD/MM/YYYY'), to_char(a.dep_time,'HH24:MI'), to_char(a.arr_time, 'HH24:MI') from tickets t, bookings b, available_flights a where b.tno = t.tno and b.tno = " +str(ticket[0]) + " and b.flightno = a.flightno and t.paid_price = a.price and b.dep_date = a.dep_date and b.fare = a.fare group by t.name, b.flightno, b.fare, b.seat, b.dep_date, a.dep_time, a.arr_time")
                        data = curs.fetchall()
                        # to print the table headings
                        print("%-20s|" % "Name" + "%-9s|" % "Flight No" + "%-4s|" % "Fare" + "%-4s|" % "Seat" + "%-10s|" % "Dep date" + "%-8s|" % "Dep time" + "%-8s" % "Arr time") 
                        space = 77 * "-"
                        print(space)
                        # this is to print the table information to standard output
                        for stuff in data:
                            print("%-20s|" % stuff[0] + "%-9s|" % stuff[1] + "%-4s|" % stuff[2] + "%-4s|" % stuff[3] + "%-10s|" % stuff[4] + "%-8s|" % stuff[5] + "%-8s" % stuff[6])
                        stall = input("Press any key to continue...")
                        invalidTicket = False
                if invalidTicket:
                    print("Please enter a valid ticket number")
        # this selection makes the user go back to the main menu       
        elif str(userSelection) == "3":
            print("Okay")
            validSelection = False
        else:
            print("Invalid input")
    
if __name__ == "__main__":
    interface()

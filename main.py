import sqlite3
import pandas as pd
import math


sqlite_con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = sqlite_con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS airports (id, 
                  ident, 
                  type, 
                  name, 
                  latitude_deg,
                  longitude_deg,
                  country,
                  municipality,
                  iata_code)''')

airports = pd.read_csv('https://davidmegginson.github.io/ourairports-data/airports.csv', sep=',')

del airports['home_link'], airports['iso_region'], airports['continent'], airports['wikipedia_link'], airports['elevation_ft'], airports['scheduled_service'], airports['gps_code'], airports['local_code'], airports['keywords']
airports = airports.loc[airports.iata_code.notnull()]    #usunięcie lotnisk, które nie posiadają kodu IATA

airports.to_sql('airports', sqlite_con, if_exists='replace')    #załadowanie DataFrame do bazy
sqlite_con.commit()

class ReportGenerator:
    def __init__(self, connection, escape_string = "(%s)", escape_string2 = "(%s)"):
        self.connection = connection
        self.escape_string = escape_string
        self.escape_string2 = escape_string2

    def calc(self, airport1, airport2):
        cursor = self.connection.cursor()
        q1 = f"SELECT name, latitude_deg, longitude_deg FROM airports WHERE iata_code={self.escape_string}"
        q2 = f"SELECT name, latitude_deg, longitude_deg FROM airports WHERE iata_code={self.escape_string2}"
        args = (airport1,)
        args2 = (airport2,)
        airport1 = cursor.execute(q1, args).fetchone()
        airport2 = cursor.execute(q2, args2).fetchone()
        return airport1, airport2

def calc_distance(x1, y1, x2, y2):
    distance = math.sqrt(math.pow((x2-x1),2) + math.pow((math.cos((x1*math.pi)/180)*(y2-y1)),2))*(40075.704/360)   #wzór na odległość pomijający krzywiznę ziemi
    distance = round(distance, 2)
    return distance

if __name__ == '__main__':
    try:
        airport1 = input("Enter IATA code for first airport\n")
        airport2 = input("Enter IATA code for second airport\n")
        rg = ReportGenerator(sqlite_con, escape_string="?", escape_string2="?")
        result = rg.calc(airport1, airport2)
        (airport1_name, airport1_lat, airport1_long), (airport2_name, airport2_lat, airport2_long) = result #rozpakowanie tuple
        distance = calc_distance(airport1_lat, airport1_long, airport2_lat, airport2_long)
        print("Distance between", airport1_name, "and", airport2_name, "is {:.2f}".format(distance), "km")
    except:
        print("Please enter correct IATA codes")
from datetime import datetime, timedelta

def print_dates(start_date, end_date):
    list = []
    current_date = datetime.strptime(start_date,'%m/%d/%Y')
    while current_date <= datetime.strptime(end_date,'%m/%d/%Y'):
        list.append(current_date.strftime('%d/%m/%Y'))
        current_date += timedelta(days=1)
    print(list)
    print(type(current_date))

# start_date = input("Enter start date: ")
# end_date = input("Enter end date: ")
start_date = "08/01/2023"
end_date = "08/10/2023"
print_dates(start_date, end_date)

import math
import datetime
from datetime import date
import copy

def median(values):
    values = sorted(values)
    if not len(values):
        return math.nan
    if len(values) % 2 == 1:
        return values[len(values)//2]
    else:
        return (values[len(values)//2]+values[int(math.ceil(len(values)/2))])/2

def working_with_data():
    missing = 0
    values = []
    budgets = []

    years = dict()
    with open('movie_metadata.csv') as file:
        index = -1
        title_year_index = -1
        budget_index = -1
        for line in file:
            splitline = line.split(',')
            if index < 0:
                index = splitline.index('duration')
                title_year_index = splitline.index('title_year')
                budget_index = splitline.index('budget')
                continue
            else:
                try:
                    values.append(float(splitline[index]))
                except ValueError:
                    missing += 1
                try:
                    budgets.append(float(splitline[budget_index].strip('$')))
                except ValueError:
                    pass
                try:
                    if int(splitline[title_year_index]) not in years:
                        years[int(splitline[title_year_index])] = [0,0,0]
                    years[int(splitline[title_year_index])] += 1
                except ValueError:
                    pass
                except IndexError:
                    pass
    print('Missing Values:', missing)

    med = median(values)
    with open('movie_metadata.csv') as file:
        with open('movie_metadata_duration_filled.csv', 'w') as output:
            title_year_index = -1
            for line in file:
                splitline = line.split(',')
                if title_year_index < 0:
                    print(line)
                    title_year_index = splitline.index('title_year')
                    plot_keywords_index = splitline.index('plot_keywords')
                    stripline = line.strip()
                    output.write(stripline + ',movie_duration_category\n')
                    continue
                else:
                    splitline[-1] = splitline[-1].strip()
                    try:
                        duration = float(splitline[index])
                    except ValueError:
                        duration = med
                        splitline[index] = str(med)
                    try:
                        year = int(float(splitline[title_year_index]))
                        if year not in years:
                            years[year] = [0,0,0]
                        if duration < 90:
                            splitline.append('1. <90')
                            years[year][0] += 1
                        elif duration >= 90 and duration <= 120:
                            splitline.append('2. 90-120')
                            years[year][1] += 1
                        else:
                            splitline.append('3. >120') 
                            years[year][2] += 1
                    except ValueError:
                        pass
                    splitline[-1] += '\n'
                    output.write(','.join(splitline))
    average = (sum(values) + med*missing) / (len(values) + missing) 
    print('Average Value', average)

    with open('movie_summary_table.csv', 'w') as output:
        output.write('year,<90,90-120,>120\n')
        for year in range(2000, datetime.datetime.now().year+1):
            if year not in years:
                years[year] = [0,0,0]
            output.write('{0},{1},{2},{3}\n'.format(year, *years[year]))
    print ('Number of films between 90 minutes and two hours releaseed in 2008:', years[2008][1])

    plot = {'love_and_death':[], 'love':[], 'death':[], 'other':[]}
    with open('movie_metadata_duration_filled.csv') as file:
        with open('movie_metadata_duration_filled_plot_category.csv', 'w') as output:
            plot_keywords_index = -1
            imdb_score_index = -1
            for line in file:
                splitline = line.split(',')
                if plot_keywords_index < 0:
                    plot_keywords_index = splitline.index('plot_keywords')
                    imdb_score_index = splitline.index('imdb_score')
                    stripline = line.strip()
                    output.write(stripline + ',movie_plot_category\n')
                    continue
                else:
                    love = splitline[plot_keywords_index].lower().find('love') >= 0
                    death = splitline[plot_keywords_index].lower().find('death') >= 0
                    try:
                        if love and death:
                            splitline.append('love_and_death')
                            plot['love_and_death'].append(float(splitline[imdb_score_index]))
                        elif love:
                            splitline.append('love')
                            plot['love'].append(float(splitline[imdb_score_index]))
                        elif death:
                            splitline.append('death')
                            plot['death'].append(float(splitline[imdb_score_index]))
                        else:
                            splitline.append('other')
                            plot['other'].append(float(splitline[imdb_score_index]))
                    except ValueError:
                        pass
                    splitline[-1] += '\n'
                    output.write(','.join(splitline))
    with open('plot_summary_table.csv', 'w') as output:
        output.write('category,average_rating\n')
        for key in plot:
            output.write('{0},{1}'.format(key, sum(plot[key])/len(plot[key])))
    print('Average rating of films in the love category: {0:.2f}'.format(sum(plot['love'])/len(plot['love'])))

    print('Median budget', int(median(budgets)))
    return missing, med

def problem_solving():
    start_date = date.fromisoformat('2018-12-31')
    end_date = date.fromisoformat('2021-01-01')
    events = dict()
    cohorts = dict()
    idToRegistration = dict()
    idToFirstPurchase = dict()
    with open('event_data.csv') as file:
        firstline = True
        for line in file:
            if firstline:
                firstline = False
                continue
            else:
                splitline = line.split(',')
                event_date = datetime.date.fromisoformat(splitline[1].split()[0])
                if splitline[2] == 'registration':
                    idToRegistration[splitline[0]] = event_date
                elif  len(splitline[3].strip()):
                    if not splitline[0] in idToFirstPurchase or idToFirstPurchase[splitline[0]] > event_date:
                        idToFirstPurchase[splitline[0]] = event_date
                index = 1
                current = copy.deepcopy(start_date)
                while current <= end_date:
                    if event_date >= current and event_date < current + datetime.timedelta(days=7):
                        if index not in events:
                            events[index] = set()
                        events[index].add(line)
                        if splitline[2] == 'registration':
                            if index not in cohorts:
                                cohorts[index] = set()
                            cohorts[index].add(splitline[0])
                    current += datetime.timedelta(days=7)
                    index += 1
    retention_rate = dict()
    print('Unique users in the cohort with ID 33: ', len(cohorts[33]))

    idToCohort = {x:key for key in cohorts for x in cohorts[key]}
    with open('retention_rate.csv', 'w') as output:
        output.write('cohort,indicator_lifetime,retention rate\n')
        for key2 in events:
            event_ids = {x.split(',')[0] for x in events[key2]}
            for key in cohorts:
                retention_rate[(key, key2)] = len(event_ids & cohorts[key])/len(cohorts[key])
                if key2 > key:
                    output.write('{0},{1},{2}\n'.format(key,key2-key,retention_rate[(key,key2)]))
    print('The 3 week retention rate for a cohort with ID 32: {0:.2f}'.format(retention_rate[(32,35)]))

    arppu = dict()
    with open('arppu.csv', 'w') as output:
        output.write('cohort,indicator_lifetime,average_revenue_per_paying_customer\n')
        for key2 in events:
            for key in cohorts:
                rev = [float(x.split(',')[3]) for x in events[key2] if len(x.split(',')[3].strip()) and x.split(',')[0] in cohorts[key]]
                try:
                    arppu[(key, key2)] = sum(rev)/len(rev)
                    if key2 > key:
                        output.write('{0},{1},{2}\n'.format(key,key2-key,arppu[(key, key2)]))
                except ZeroDivisionError:
                    pass
    print('The 3-week ARPPU of a cohort with ID 31: {0:.2f}'.format(arppu[(31,34)]))

    times_to_first = [(idToFirstPurchase[key]-idToRegistration[key]).total_seconds() for key in idToFirstPurchase]
    print('Median time between user registration and first purchase: {0} seconds'.format(int(median(times_to_first))))

if __name__ == '__main__':
    working_with_data()
    problem_solving()

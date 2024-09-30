
missing_keywords = []
found_keywords = []

the_keywords = [
    'strategy',
    'roadmap',
    'Analytics',
    'Customer',
    'Technical',
    'Entrepreneurial',
    'Cross-functional',
    'Software',
    'Communication',
    'Leadership',
    'Influencing',
    'execution'
]



def generate_keywords(fname):
    file = open(fname, "r")
    if file is not None:
        the_resume = file.read().lower()

        count=0
        for index, keyword in enumerate(the_keywords, start=1):
            if keyword.lower() in the_resume:
                found_keywords.append(keyword)
                print(f'{index}. {keyword}')
                count=count+1
        print("Found " + str(count) + " keywords")

        print("------\n")

        count=0
        for index, keyword in enumerate(the_keywords, start=1):
            if keyword.lower() not in the_resume:
                missing_keywords.append(keyword)
                print(f'{index}. {keyword}')
                count=count+1
        print(str(count) + " missing keywords")

        

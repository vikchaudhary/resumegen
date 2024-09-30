
missing_keywords = []


the_keywords = [
    'Product Operations',
    'Product priorities',
    'Business management',
    'Governance',
    'Cross-functional collaboration',
    'Product Management',
    'Engineering',
    'Finance',
    'Sales',
    'Marketing',
    'Operations',
    'Google Cloud',
    'Digital transformation',
    'Infrastructure',
    'Platform',
    'Industry solutions',
    'Product roadmap',
    'Goal execution',
    'Alignment',
    'Business operations',
    'Continuous improvement',
    'Business cadence',
    'Business growth',
    'Pricing',
    'Agreement',
    'People management',
    'Financial model',
    'MBA',
    'Partner relationship management',
    'Product strategy',
    'SaaS',
    'Cloud',
    'B2B',
    'Project management',
    'Stakeholder',
    'Initiative',
    'Strategy',
    'Results'
]





file = open("/Users/vik/Downloads/Vik Chaudhary Resume for Google Prod Ops.txt", "r")
if file is not None:
    the_resume = file.read().lower()
    count=0

    for index, keyword in enumerate(the_keywords, start=1):
        if keyword.lower() not in the_resume:
            missing_keywords.append(keyword)
            print(f'{index}. {keyword}')
            count=count+1
print ("Found " + str(count) + " missing keywords")
# print(missing_keywords)
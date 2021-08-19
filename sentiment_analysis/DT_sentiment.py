import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn import tree

filename_training=str(sys.argv[1])
filename_test=str(sys.argv[2])

col_names=['ID','tweet','sentiment']
data_training= pd.read_csv(filename_training, sep='\t',names=col_names)
data_test = pd.read_csv(filename_test, sep='\t',names=col_names)
#minimum number to continue splitting
#min_split= int(0.01*len(data_training))

for t in range(2):
    if t==0:
        data = data_training
    else:
        data = data_test
    #Data cleaning (tweets) 
    count=0
    x_vector=[]
    empty_tweets=[]
    for i in data['tweet']:
        aux_tweet =''
        for j in i.split():
            #exclude URLs
            if j.startswith("http://") or j.startswith("https://"):
                continue
            #delete 'junk' characters
            new_word=''
            for k in j:
                if ord(k) in range(48,58) or ord(k) in range(65,91) or ord(k) in range(97,123) or k in '@#$%_':
                    new_word=new_word+k
            #valid words
            if len(new_word) >=2:
                aux_tweet = aux_tweet+new_word+' '
                 
        #remove the space added at the end of the tweet
        aux_tweet = aux_tweet.rstrip()
        
        #check if tweet is empty and save the position
        if aux_tweet == '':
            empty_tweets.append(count)
        
        x_vector.append(aux_tweet)
        count +=1 
    
    #create the Y vector
    y_vector = list(data['sentiment'])
    id_vector = list(data['ID'])
    #check if the dimension of x_vector, y_vector and instance vector are the same
    if len(x_vector) != len(y_vector):
        for i in empty_tweets:
            y_vector.pop(i)
            id_vector.pop(i)
    
    if t==0:
        x_training = x_vector.copy()
        y_training = y_vector.copy()
        id_training = id_vector.copy()
    else:
        x_test = x_vector.copy()
        y_test = y_vector.copy()
        id_test = id_vector.copy()

# vectorize and fit with training data
vectorize = CountVectorizer(token_pattern=r'[a-zA-Z0-9@#\$%_]+',max_features=1000,lowercase=False)
X_train_bag_of_words = vectorize.fit_transform(x_training)
X_test_bag_of_words = vectorize.transform(x_test)


clf = tree.DecisionTreeClassifier(min_samples_leaf=0.01,criterion='entropy',random_state=0)
model = clf.fit(X_train_bag_of_words, y_training)
predicted_y = model.predict(X_test_bag_of_words)



for i in range(len(id_test)):
    print(id_test[i],predicted_y[i])





import pandas as pd
from aspect_extract_parser import get_clues
import pickle
from nltk.corpus import stopwords



data = pd.read_excel (r'comments.xlsx') 
df = pd.DataFrame(data)
comments = df.ix[:767,1]



def frequent_key_words_write():
	frequent_words={}
	frequent_words_senti={}
	for i,comment in enumerate(comments):
		if(not isinstance(comment, str)):
			continue
		key_words,key_senti_words = get_clues(comment)
		print(key_words)
		print(key_senti_words)
		for word in key_words:
			if word not in frequent_words:
				frequent_words[word]=1
			else:
				frequent_words[word]+=1
		for word in key_senti_words:
			if(word not in frequent_words_senti):
				frequent_words_senti[word]=1
			else:
				frequent_words_senti[word]+=1

	frequent_words = sorted(frequent_words.items(), key=lambda x: x[1], reverse=True)
	frequent_words_senti = sorted(frequent_words_senti.items(), key=lambda x: x[1], reverse=True)
	output = open('frequent_key_words.pkl', 'wb')
	output2 = open('frequent_key_words_senti.pkl','wb')
	pickle.dump(frequent_words, output)
	pickle.dump(frequent_words_senti,output2)
	output.close()
	output2.close()

def frequent_bigrams_write():
	frequent_bigrams={}
	stop_words = set(stopwords.words('english'))
	for i,comment in enumerate(comments):
		if(not isinstance(comment, str)):
			continue
		words = comment.split() 
		pairs =[]
		for i in range(len(words)-1):
			if words[i] not in stop_words and words[i+1] not in stop_words and words[i].isalnum() and words[i+1].isalnum():
				print(words[i],words[i+1])
				pairs.append((words[i], words[i+1]))
		for pair in pairs:
			if pair in frequent_bigrams:
				frequent_bigrams[pair]+=1
			else:
				frequent_bigrams[pair]=1
		
	frequent_bigrams = sorted(frequent_bigrams.items(), key=lambda x: x[1], reverse=True)
	output = open('frequent_bigrams.pkl', 'wb')
	pickle.dump(frequent_bigrams, output)
	output.close()

def frequent_bigrams_read():
	pkl_file = open('frequent_bigrams.pkl', 'rb')
	mydict = pickle.load(pkl_file)
	pkl_file.close()
	return mydict

def frequent_key_words_read():
	pkl_file = open('frequent_key_words.pkl', 'rb')
	pkl_file_2 = open('frequent_key_words_senti.pkl','rb')
	mydict = pickle.load(pkl_file)
	mydict2 = pickle.load(pkl_file_2)
	pkl_file.close()
	pkl_file_2.close()
	return mydict,mydict2


frequent_key_words_write()
frequent_bigrams_write()




frequent_words, frequent_words_senti = frequent_key_words_read()
frequent_bigrams = frequent_bigrams_read()

print("\n------------(Bigrams - top 150)------------")
print(frequent_bigrams[:150])
print("\n------------(Aspect clues - top 150)------------")
print(frequent_words[:150])
print("\n------------(Aspect clues(applying sentinet) - top 150)------------")
print(frequent_words_senti[:150])

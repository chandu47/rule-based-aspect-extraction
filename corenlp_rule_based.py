import stanfordnlp
from pycorenlp import StanfordCoreNLP
from senticnet.senticnet import SenticNet
import spacy
import time
from nltk.corpus import stopwords 

def get_clues(text):
	text = text
	print("*--------(%s)-------------*" %(text))
	print(type(text))
	nlp = StanfordCoreNLP('http://localhost:9001')
	stop_words = set(stopwords.words('english'))

	'''
		Method to remove numbers appended at last
	'''
	dep_parse = nlp.annotate(text,
	                   properties={
	                       'annotators': 'depparse',
	                       'outputFormat': 'json',
	                       'timeout': 10000,
	                   })

	pos = nlp.annotate(text,
	                   properties={
	                       'annotators': 'lemma',
	                       'outputFormat': 'json',
	                       'timeout': 10000,
	                   })

	sn = SenticNet()
	word_to_dep = [{} for i in range(len(dep_parse['sentences']))]
	word_to_par = [{} for i in range(len(dep_parse['sentences']))]
	word_to_pos = [{} for i in range(len(dep_parse['sentences']))]
	word_to_lemma = [{} for i in range(len(dep_parse['sentences']))]
	word_to_child = [{} for i in range(len(dep_parse['sentences']))]
	sents=[[] for i in range(len(dep_parse['sentences']))]
	index_to_word = {}

	'''
		Constructing dicts for maintaining the dependencies among words. 
	'''

	'''
		Appending each word by occurence number to maintain distinct word count
	'''
	#print(dep_parse['sentences'])
	print("********")
	for i,sent in enumerate(dep_parse['sentences']):
		for dep in sent['basicDependencies']:
			word_to_dep[i][dep['dependentGloss']+str(dep['dependent'])] = dep['dep']
			word_to_par[i][dep['dependentGloss']+str(dep['dependent'])] = dep['governorGloss']+str(dep['governor'])
			index_to_word[dep['dependentGloss']+str(dep['dependent'])] = dep['dependentGloss']

			if(dep['governorGloss']+str(dep['governor']) not in word_to_child[i]):
				word_to_child[i][dep['governorGloss']+str(dep['governor'])] = []
			if(dep['dependentGloss']+str(dep['dependent']) not in word_to_child[i]):
				word_to_child[i][dep['dependentGloss']+str(dep['dependent'])] = []
			word_to_child[i][dep['governorGloss']+str(dep['governor'])].append(dep['dependentGloss']+str(dep['dependent']))
			sents[i].append(dep['dependentGloss']+str(dep['dependent']))
		word_to_dep[i]['ROOT0'] = 'root'
		word_to_par[i]['ROOT0'] = 'root'
		

	for i,sent in enumerate(pos['sentences']):
		for pos_tagger in sent['tokens']:
			word_to_pos[i][pos_tagger['word']] = pos_tagger['pos']
			word_to_lemma[i][pos_tagger['word']] = pos_tagger['lemma'] 
		word_to_pos[i]['ROOT'] = 'root'
		word_to_lemma[i]['ROOT'] = 'root'

	'''
		Displaying the deps
	'''

	##Implemeting rules to extract aspects
	for i,sent in enumerate(sents):
		if(__name__=='__main__'):
			print(word_to_dep[i],word_to_par[i],word_to_pos[i])
			print("Children==>")
			print(word_to_child[i])



	aspects = []
	for i,sent in enumerate(sents):
		for word in sent:
			'''
				Rule 0
			'''
			if('subj' in word_to_dep[i][word]):
					for child in word_to_child[i][word_to_par[i][word]]:
						if('amod' in word_to_dep[i][child] or 'advmod' in word_to_dep[i][child]):
							aspects.append(word_to_par[i][word])
							if(__name__=='__main__'):
								print("Rule 0 triggered.")
			'''
				Rule 1 (without sub): Very big to hold.
			'''
			if(word_to_dep[i][word] == 'xcomp' and ('JJ' in word_to_pos[i][index_to_word[word_to_par[i][word]]] or 'RB' in word_to_pos[i][index_to_word[word_to_par[i][word]]])):
				if(__name__=='__main__'):
					print("Rule 1 triggered")
				aspects.append(word_to_par[i][word])
				

			'''
				Rule 2 (without subj): Not to mention the price of the phone
			'''
			if(word_to_dep[i][word]=='dobj' and 'VB' in word_to_pos[i][index_to_word[(word_to_par[i][word])]] and ('NN' in word_to_pos[i][index_to_word[(word)]] or 'JJ' in word_to_pos[i][index_to_word[(word)]])):
				aspects.append(word)
				if(__name__=='__main__'):
					print("Rule 2 triggered")
					print(word)

			'''
				Rule 3 (without subj): Love the sleekness of the player
			'''
		
			if('NN' in word_to_pos[i][index_to_word[(word)]] and word_to_dep[i][word]=='nmod'):
				aspects.append(word_to_par[i][word])
				if(__name__=='__main__'):
					print("Rule 3 triggered")
					print(word_to_par[i][word])


				'''
				Rule 4 (with sub): The battery lasts little 
				two aspects 
			'''
			if(word_to_dep[i][word]=='advmod' or word_to_dep[i][word]=='amod' or word_to_dep[i][word]=='advcl') and ('VB' in word_to_pos[i][index_to_word[(word_to_par[i][word])]]):
				aspects.append(word_to_par[i][word])
				for word2 in sent:
					if(word2 != word and word_to_dep[i][word2]=='nsubj' and word_to_par[i][word2] == word_to_par[i][word] and ('NN' in word_to_pos[i][index_to_word[word2]] or 'JJ' in word_to_pos[i][index_to_word[word2]])):
						aspects.append(word2)
						if(__name__=='__main__'):
							print("Rule 4 triggered")
							print(word2)
				'''
				Rule 5 (with sub): I like the lens of this camera
			'''
			if('NN' in word_to_pos[i][index_to_word[(word)]] and word_to_dep[i][word]=='dobj'):
				if(__name__=='__main__'):
					print("Rule 5 triggered")
					print(word)
				try:
					concept_info = sn.concept((word))
					print("present in senticnet")
				except KeyError:
					print("Yay")	
					aspects.append(word)

			'''
				Rule 6 : I like the beauty of the screen.
				Check if senticnet condition should be added
			'''
			if('NN' in word_to_pos[i][index_to_word[(word)]] and word_to_dep[i][word]=='dobj'):
				try:
					concept_info = sn.concept((word))
					aspects.append(word)
					print("yay!")
				except KeyError:	
					print("oops, not there in SenticNet")
				for word2 in sent:
					if(word2 != word and word_to_par[i][word2]==word and 'NN' in word_to_pos[i][index_to_word[(word2)]]):
						aspects.append(word2)
						if(__name__=='__main__'):	
							print("Rule 6 triggered.")
							print(word2)
			'''
				Rule 7 : I would like to comment on the camera of this phone. 
			
			'''	
			if(word_to_dep[i][word] == 'xcomp'):
				try:
					concept_info = sn.concept((word))
					aspects.append(word)
					print("yay!")
				except KeyError:	
					print("oops, not there in SenticNet")
				for child in word_to_child[i][word]:
					if('NN' in word_to_pos[i][index_to_word[child]]):
						aspects.append(child)
						if(__name__=='__main__'):
							print("Rule 7 triggered.")
							print(word)
							print(child)
			'''
				Rule 8 : The car is expensive.
			'''	
			if(word_to_dep[i][word]=='nsubj'):
				for word2 in sent:
					if(word2 != word and word_to_dep[i][word2] == 'cop' and word_to_par[i][word2]==word_to_par[i][word]):
						aspects.append(word_to_par[i][word])
						if(__name__=='__main__'):
							print("Rule 8 triggered")
							print(word_to_par[i][word])
			'''			
				Rule 9 : The camera is nice.
			'''
			if(word_to_dep[i][word]=='nsubj' and 'NN' in word_to_pos[i][index_to_word[(word)]]):
				for word2 in sent:
					if(word2 != word and word_to_dep[i][word2] == 'cop' and word_to_par[i][word2]==word_to_par[i][word]):
						aspects.append(word)
						if(__name__=='__main__'):
							print("Rule 9 triggered")
							print(word)

			'''
				Rule 10 : The phone is very lightweight to carry.
			'''
			if(word_to_dep[i][word]=='cop'):
				for word2 in sent:
					if(word2 != word and 'VB' in word_to_pos[i][index_to_word[(word2)]] and word_to_par[i][word]==word_to_par[i][word2]):
						aspects.append(word2)
						if(__name__=='__main__'):	
							print("Rule 10 triggered.")
							print(word2)

			'''
				Extracting mods of dobjs

			'''
			if(word_to_dep[i][word]=='dobj'):
				for child in word_to_child[i][word]:
					if('mod' in word_to_dep[i][child] and 'JJ' in word_to_pos[i][index_to_word[(child)]]):
						aspects.append(child)
			'''
				Rule 11 : Checking for conjuctions
			'''
		for asp in aspects:
			for word in sent:
				if(word_to_dep[i][word]=='conj' and word_to_par[i][word]==asp):
					aspects.append(word)
					if(__name__=='__main__'):	
						print("Rule conj triggered.")
						print(word)


	finalIAC = set(aspects)
	finalIAC = [index_to_word[f] for f in finalIAC]
	finalIAC = [w for w in finalIAC if not w in stop_words]


	finalSenti = []
	for iac in finalIAC:
		try:
			concept_info = sn.concept((iac))
			finalSenti.append(iac)
		except KeyError:	
			print("No word available for "+iac)

	return finalIAC,finalSenti

if __name__ == '__main__':
	print(get_clues("sometimes i find bad thing like in a bag of orange i find one bad can affect the other . need to check before put them inside the bag . thank"))
	




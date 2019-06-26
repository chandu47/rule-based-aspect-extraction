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
	aspect_result = [[] for i in range(len(dep_parse['sentences']))]

	'''
		Constructing dicts for maintaining the dependencies among words. 
	'''

	'''
		Appending each word by occurence number to maintain distinct word count
	'''
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
			print(word_to_dep[i],word_to_par[i],word_to_pos[i],word_to_lemma[i])
			print("Children==>")
			print(word_to_child[i])



	for i,sent in enumerate(sents):
		token_t = word_to_child[i]['ROOT0'][0]
		is_sub = False
		token_h = None
		for child in word_to_child[i][token_t]:
			if 'subj' in word_to_dep[i][child]:
				is_sub = True
				token_h = child

		#If subject noun relationship present
		if is_sub:
			"""
				Rule 0: if any adv or adj modifies the token t.

			"""
			for child in word_to_child[i][token_t]:
				if('amod' in word_to_dep[i][child] or 'advmod' in word_to_dep[i][child]):
					try:
						concept_info = sn.concept(index_to_word[child])
						aspect_result[i].append(token_t)
						if __name__ == '__main__':
							print("Rule 1 triggered.")
							print("present in senticnet")
					except KeyError:
						print("OOps")	
						

			"""
				Rule 1: The battery lasts little.

			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='advmod' or word_to_dep[i][child]=='amod' or word_to_dep[i][child]=='advcl') and ('VB' in word_to_pos[i][index_to_word[token_t]]):
					aspect_result[i].append(token_t)
					aspect_result[i].append(token_h)
					if __name__ == '__main__':
						print("Rule 1 triggered.")
						print(token_t)
						print(token_h)

			"""
				Rule 2: I like the beauty of the screen (and I like the lens of this camera). 

			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='dobj' and 'NN' in word_to_pos[i][index_to_word[child]]):
					aspect_result[i].append(child)
					if __name__ == '__main__':
						print(child)
					try:
						concept_info = sn.concept(index_to_word[child])
						if __name__ == '__main__':
							print("Rule 2 triggered")
						for grandchild in word_to_child[i][child]:
							if('NN' in word_to_pos[i][index_to_word[grandchild]]):
								aspect_result[i].append(grandchild)
								print(grandchild)
					except KeyError:
						print("OOps")

			"""
				Rule 3: I would like to comment on the camera of this phone.
	
			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='xcomp'):
					try:
						sn.concept(index_to_word[child])
						aspect_result[i].append(child)
						if __name__ == '__main__':
							print(child)
					except KeyError:
						print("OOps")
					for grandchild in word_to_child[i][child]:
						if('NN' in word_to_pos[i][index_to_word[grandchild]]):
							aspect_result[i].append(grandchild)
							if __name__ == '__main__':
								print(grandchild)
								print("Rule 3 triggered.")

			"""
				Rule 4: The car is expensive.

			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='cop'):
					try:
						sn.concept(word_to_lemma[i][index_to_word[token_t]])
						aspect_result[i].append(token_t)
						if __name__ == '__main__':
							print("Rule 4 triggered")
							print(token_t)
					except KeyError:
						pass
			"""
				Rule 5: The camera is nice

			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='cop' and 'NN' in word_to_pos[i][index_to_word[token_h]]):
					aspect_result[i].append(token_h)
					if __name__ == '__main__':
						print("Rule 5 triggered.")
						print(token_h)

			"""
				Rule 6: 

			"""
			for child in word_to_child[i][token_t]:
				if(word_to_dep[i][child]=='cop'):
					for child2 in word_to_child[i][token_t]:
						if(child!=child2 and 'VB' in word_to_pos[i][index_to_word[child2]]):
							try:
								sn.concept(index_to_word[token_t])
								sn.concept(index_to_word[child2])
								aspect_result[i].append(token_t)
								aspect_result[i].append(child2)
								if __name__ == '__main__':
									print("rule 6 trigg")
									print(token_t)
									print(child2)
							except KeyError:
								pass
		else:
			"""
				Rule 7:Very big to hold.

			"""
			for word in sent:
				if('RB' in word_to_pos[i][index_to_word[word]] or 'JJ' in word_to_pos[i][index_to_word[word]]):

					for child in word_to_child[i][word]:
						if(word_to_dep[i][child] == 'xcomp' or word_to_dep[i][child]=='ccomp'):
							aspect_result[i].append(word)
							if __name__ == '__main__':
								print("Rule 7 triggered")
								print(word)
			
			"""
				Rule 8: Love the sleekness of the player.
			"""
			for word in sent:
				for child in word_to_child[i][word]:
					if('NN' in word_to_pos[i][index_to_word[child]] and word_to_dep[i][child] == 'nmod'):
						for grandchild in word_to_child[i][child]:
							if('IN' in word_to_pos[i][index_to_word[grandchild]]):
								aspect_result[i].append(word)
								aspect_result[i].append(child)
								if __name__ == '__main__':
									print(word)
									print(child)
									print("Rule 8 triggered.")

			"""
				Rule 9: Not to mention the price of the phone.

			"""
			for word in sent:
				for child in word_to_child[i][word]:
					if(word_to_dep[i][child]=='dobj'):
						aspect_result[i].append(child)
						if __name__ == '__main__':
							print(child)
							print("Rule 9 triggered")


			'''
				Rule 11 : Checking for conjuctions
			'''
		for asp in aspect_result[i]:
			for word in sent:
				if(word_to_dep[i][word]=='conj' and word_to_par[i][word]==asp):
					aspect_result[i].append(word)
					if(__name__=='__main__'):	
						print("Rule conj triggered.")
						print(word)


	finalIAC = [set(aspect_result[i]) for i in range(len(sents))]
	finalIAC = [[index_to_word[w] for w in finalIAC[i]] for i in range(len(sents))]

	print(finalIAC)
	singleFinalIAC=[]
	for i in range(len(sents)):
		for w in finalIAC[i]:
			if w not in stop_words:
				singleFinalIAC.append(w)
	print(singleFinalIAC)

	finalSenti = []
	for iac in singleFinalIAC:
		try:
			concept_info = sn.concept((iac))
			finalSenti.append(iac)
		except KeyError:	
			print("No word available for "+iac)

	return singleFinalIAC,finalSenti


if __name__ == '__main__':
	print(get_clues("package too large . only two of us can not use before it goes bad ."))
	




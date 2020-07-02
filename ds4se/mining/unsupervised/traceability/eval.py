# AUTOGENERATED! DO NOT EDIT! File to edit: dev/3.3_mining.unsupervised.traceability.eval.ipynb (unless otherwise specified).

__all__ = ['BasicSequenceVectorization', 'Word2VecSeqVect', 'LoadLinks', 'VectorEvaluation',
           'SupervisedVectorEvaluation', 'Doc2VecSeqVect']

# Cell
# Imports
import numpy as np
import gensim
import pandas as pd
from itertools import product
from random import sample
import functools
import os

# Cell
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Cell
class BasicSequenceVectorization():
    '''Implementation of the class sequence-vanilla-vectorization other classes can inheritance this one'''
    def __init__(self, params):

        self.df_source = pd.read_csv(params['source_path'], names=['ids', 'text'], header=None, sep=' ')
        self.df_target = pd.read_csv(params['target_path'], names=['ids', 'text'], header=None, sep=' ')
        self.df_all_system = pd.read_csv(params['system_path'], names=['ids', 'text'],
                                         header=0, index_col=0, sep=',')
        self.params = params
        self.df_nonground_link = None
        self.df_ground_link = None

        self.documents = [doc.split() for doc in self.df_all_system['text'].values] #Preparing Corpus
        self.dictionary = corpora.Dictionary( self.documents ) #Preparing Dictionary


        #This can be extended for future metrics <---------------------
        self.dict_labels = {
            DistanceMetric.COS:[DistanceMetric.COS, SimilarityMetric.COS_sim],
            SimilarityMetric.Pearson:[SimilarityMetric.Pearson],
            DistanceMetric.EUC:[DistanceMetric.EUC, SimilarityMetric.EUC_sim],
            DistanceMetric.WMD:[DistanceMetric.WMD, SimilarityMetric.WMD_sim],
            DistanceMetric.SCM:[DistanceMetric.SCM, SimilarityMetric.SCM_sim],
            DistanceMetric.MAN:[DistanceMetric.MAN, SimilarityMetric.MAN_sim]
        }


    def ground_truth_processing(self, path_to_ground_truth):
        'Optional class when corpus has ground truth'
        ground_truth = open(path_to_ground_truth,'r')
        #Organizing The Ground Truth under the given format
        ground_links = [ [(line.strip().split()[0], elem) for elem in line.strip().split()[1:]] for line in ground_truth]
        ground_links = functools.reduce(lambda a,b : a+b,ground_links) #reducing into one list
        assert len(ground_links) ==  len(set(ground_links)) #To Verify Redundancies in the file
        return ground_links

    def samplingLinks(self, sampling = False, samples = 10):
        source = [os.path.basename(elem) for elem in self.df_source['ids'].values ]
        target = [os.path.basename(elem) for elem in self.df_target['ids'].values ]

        if sampling:
            links = sample( list( product( source , target ) ), samples)
        else:
            links = list( product( source , target ))

        return links

    def cos_scipy(self, vector_v, vector_w):
        cos =  distance.cosine( vector_v, vector_w )
        return [cos, 1.-cos]

    def euclidean_scipy(self, vector_v, vector_w):
        dst = distance.euclidean(vector_v,vector_w)
        return [dst, 1./(1.+dst)] #Computing the inverse for similarity

    def manhattan_scipy(self, vector_v, vector_w):
        dst = distance.cityblock(vector_v,vector_w)
        n = len(vector_v)
        return [dst, 1./(1.+dst)] #Computing the inverse for similarity

    def pearson_abs_scipy(self, vector_v, vector_w):
        '''We are not sure that pearson correlation works well on doc2vec inference vectors'''
        corr, _ = pearsonr(x, y)
        return [abs(corr)] #Absolute value of the correlation


    def computeDistanceMetric(self, links, metric_list):
        '''Metric List Iteration'''

        metric_labels = [ self.dict_labels[metric] for metric in metric_list] #tracking of the labels
        distSim = [[link[0], link[1], self.distance( metric_list, link )] for link in links] #Return the link with metrics
        distSim = [[elem[0], elem[1]] + elem[2] for elem in distSim] #Return the link with metrics

        return distSim, functools.reduce(lambda a,b : a+b, metric_labels)

    def ComputeDistanceArtifacts(self, metric_list, sampling = False , samples = 10):
        '''Acticates Distance and Similarity Computations
        @metric_list if [] then Computes All metrics
        @sampling is False by the default
        @samples is the number of samples (or links) to be generated'''
        links_ = self.samplingLinks( sampling, samples )

        docs, metric_labels = self.computeDistanceMetric( metric_list=metric_list, links=links_) #checkpoints
        self.df_nonground_link = pd.DataFrame(docs, columns =[self.params['names'][0], self.params['names'][1]]+ metric_labels) #Transforming into a Pandas
        logging.info("Non-groundtruth links computed")
        pass


    def SaveLinks(self, grtruth=False, sep=' ', mode='a'):
        timestamp = datetime.timestamp(datetime.now())
        path_to_link = self.params['saving_path'] + '['+ self.params['system'] + '-' + str(self.params['vectorizationType']) + '-' + str(self.params['linkType']) + '-' + str(grtruth) + '-{}].csv'.format(timestamp)

        if grtruth:
            self.df_ground_link.to_csv(path_to_link, header=True, index=True, sep=sep, mode=mode)
        else:
            self.df_nonground_link.to_csv(path_to_link, header=True, index=True, sep=sep, mode=mode)

        logging.info('Saving in...' + path_to_link)
        pass

    def findDistInDF(self, g_tuple):
        dist = self.df_ground_link[self.df_ground_link[self.params['names'][0]].str.contains( g_tuple[0][:g_tuple[0].find('.')] + '-' )
                     & self.df_ground_link[self.params['names'][1]].str.contains(g_tuple[1][:g_tuple[1].find('.')]) ]
        return dist.index.values

    def MatchWithGroundTruth(self, path_to_ground_truth ):
        self.df_ground_link = self.df_nonground_link.copy()

        matchGT = [ self.findDistInDF( g ) for g in self.ground_truth_processing(path_to_ground_truth)]
        matchGT = functools.reduce(lambda a,b : np.concatenate([a,b]), matchGT)

        self.df_ground_link[self.params['names'][2]] = 0
        new_column = pd.Series(np.full([len(matchGT)], 1 ), name=self.params['names'][2], index = matchGT)
        self.df_ground_link.update(new_column)
        logging.info("Groundtruth links computed")

        pass

# Cell
class Word2VecSeqVect(BasicSequenceVectorization):

    def __init__(self, params):
        super().__init__(params)
        self.new_model = gensim.models.Word2Vec.load( params['path_to_trained_model'] )
        self.new_model.init_sims(replace=True)  # Normalizes the vectors in the word2vec class.
        #Computes cosine similarities between word embeddings and retrieves the closest
        #word embeddings by cosine similarity for a given word embedding.
        self.similarity_index = WordEmbeddingSimilarityIndex(self.new_model.wv)
        #Build a term similarity matrix and compute the Soft Cosine Measure.
        self.similarity_matrix = SparseTermSimilarityMatrix(self.similarity_index, self.dictionary)

        self.dict_distance_dispatcher = {
            DistanceMetric.COS: self.cos_scipy,
            SimilarityMetric.Pearson: self.pearson_abs_scipy,
            DistanceMetric.WMD: self.wmd_gensim,
            DistanceMetric.SCM: self.scm_gensim
        }

    def wmd_gensim(self, sentence_a, sentence_b ):
        wmd = self.new_model.wv.wmdistance(sentence_a, sentence_b)
        return [wmd, self.wmd_similarity(wmd)]

    def wmd_similarity(self, dist):
        return 1./( 1.+float( dist ) ) #Associated Similarity

    def scm_gensim(self, sentence_a, sentence_b ):
        '''Compute SoftCosine Similarity of Gensim'''
        #Convert the sentences into bag-of-words vectors.
        sentence_1 = self.dictionary.doc2bow(sentence_a)
        sentence_2 = self.dictionary.doc2bow(sentence_b)

        #Return the inner product(s) between real vectors / corpora vec1 and vec2 expressed in a non-orthogonal normalized basis,
        #where the dot product between the basis vectors is given by the sparse term similarity matrix.
        scm_similarity = self.similarity_matrix.inner_product(sentence_1, sentence_2, normalized=True)
        return [1-scm_similarity, scm_similarity]

    def distance(self, metric_list,link):
        '''Iterate on the metrics'''
        #Computation of sentences can be moved directly to wmd_gensim method if we cannot generalize it for
        #the remaining metrics
        sentence_a = self.df_source[self.df_source['ids'].str.contains(link[0])]['text'].values[0].split()
        sentence_b = self.df_target[self.df_target['ids'].str.contains(link[1])]['text'].values[0].split()

        dist = [ self.dict_distance_dispatcher[metric](sentence_a,sentence_b) for metric in metric_list]
        logging.info("Computed distances or similarities "+ str(link) + str(dist))
        return functools.reduce(lambda a,b : a+b, dist) #Always return a list


# Cell
def LoadLinks(timestamp, params, grtruth=False, sep=' ' ):
    '''Returns a pandas from a saved link computation at a give timestamp
    @timestamp is the version of the model for a given system'''

    path= params['saving_path'] + '['+ params['system'] + '-' + str(params['vectorizationType']) + '-' + str(params['linkType']) + '-' + str(grtruth) + '-{}].csv'.format(timestamp)

    logging.info("Loading computed links from... "+ path)

    return pd.read_csv(path, header=0, index_col=0, sep=sep)

# Cell
class VectorEvaluation():
    '''Approaches Common Evaluations and Interpretations (statistical analysis)'''
    def __init__(self, sequenceVectorization):
        self.seqVect = sequenceVectorization

# Cell
class SupervisedVectorEvaluation(VectorEvaluation):
    def __init__(self, sequenceVectorization, similarity):
        super().__init__(sequenceVectorization)
        self.y_test = sequenceVectorization.df_ground_link['Linked?'].values
        self.y_score = sequenceVectorization.df_ground_link[similarity].values
        self.label = str(sequenceVectorization.params['vectorizationType'])+'-'+str(similarity)
        pass

    def Compute_precision_recall_gain(self):
        '''One might choose PRG if there is little interest in identifying false negatives '''
        prg_curve = prg.create_prg_curve(self.y_test, self.y_score)
        auprg = prg.calc_auprg(prg_curve)
        prg.plot_prg(prg_curve)
        logging.info('auprg:  %.3f' %  auprg)
        logging.info("compute_precision_recall_gain Complete")
        pass

    def Compute_avg_precision(self):
        '''Generated precision-recall curve'''
        %matplotlib inline
        # calculate the no skill line as the proportion of the positive class
        no_skill = len(self.y_test[self.y_test==1]) / len(self.y_test)
        plt.plot([0, 1], [no_skill, no_skill], linestyle='--', label='No Skill') #reference curve
        precision, recall, _ = precision_recall_curve(self.y_test, self.y_score) #compute precision-recall curve
        plt.plot(recall, precision, marker='.', label = self.label) #plot model curve
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.legend() #show the legend
        plt.show() #show the plot

        average_precision = average_precision_score(self.y_test, self.y_score)
        auc_score = auc(recall, precision)
        logging.info('Average precision-recall score: {0:0.2f}'.format(average_precision))
        logging.info('Precision-Recall AUC: %.3f' % auc_score)
        #logging.info("compute_precision_recall_gain Complete")
        pass

    def Compute_roc_curve(self):
        %matplotlib inline
        plt.plot([0, 1], [0, 1], linestyle='--', label='No Skill') #reference curve
        fpr, tpr, _ = roc_curve(self.y_test, self.y_score) #compute roc curve
        plt.plot(fpr, tpr, marker='.', label=self.label) #plot model curve
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend() #show the legend
        plt.show() #show the plot

        roc_auc = roc_auc_score(self.y_test, self.y_score)
        logging.info('ROC AUC %.3f' % roc_auc)

        pass

# Cell
class Doc2VecSeqVect(BasicSequenceVectorization):

    def __init__(self, params):
        super().__init__(params)
        self.new_model = gensim.models.Doc2Vec.load( params['path_to_trained_model'] )
        self.new_model.init_sims(replace=True)  # Normalizes the vectors in the word2vec class.
        self.df_inferred_src = None
        self.df_inferred_trg = None

        self.dict_distance_dispatcher = {
            DistanceMetric.COS: self.cos_scipy,
            SimilarityMetric.Pearson: self.pearson_abs_scipy,
            DistanceMetric.EUC: self.euclidean_scipy,
            DistanceMetric.MAN: self.manhattan_scipy
        }

    def distance(self, metric_list, link):
        '''Iterate on the metrics'''
        ν_inferredSource = list(self.df_inferred_src[self.df_inferred_src['ids'].str.contains(link[0])]['inf-doc2vec'])
        w_inferredTarget = list(self.df_inferred_trg[self.df_inferred_trg['ids'].str.contains(link[1])]['inf-doc2vec'])

        dist = [ self.dict_distance_dispatcher[metric](ν_inferredSource,w_inferredTarget) for metric in metric_list]
        logging.info("Computed distances or similarities "+ str(link) + str(dist))
        return functools.reduce(lambda a,b : a+b, dist) #Always return a list

    def computeDistanceMetric(self, links, metric_list):
        '''It is computed the cosine similarity'''

        metric_labels = [ self.dict_labels[metric] for metric in metric_list] #tracking of the labels
        distSim = [[link[0], link[1], self.distance( metric_list, link )] for link in links] #Return the link with metrics
        distSim = [[elem[0], elem[1]] + elem[2] for elem in distSim] #Return the link with metrics

        return distSim, functools.reduce(lambda a,b : a+b, metric_labels)


    def InferDoc2Vec(self, steps=200):
        '''Activate Inference on Target and Source Corpus'''
        self.df_inferred_src = self.df_source.copy()
        self.df_inferred_trg = self.df_target.copy()

        self.df_inferred_src['inf-doc2vec'] =  [self.new_model.infer_vector(artifact.split(),steps=steps) for artifact in self.df_inferred_src['text'].values]
        self.df_inferred_trg['inf-doc2vec'] =  [self.new_model.infer_vector(artifact.split(),steps=steps) for artifact in self.df_inferred_trg['text'].values]

        logging.info("Infer Doc2Vec on Source and Target Complete")

#!/usr/bin/env python3
# Copyright (C) <2018-2022>  <Agence Data Services, DSI Pôle Emploi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Libs unittest
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# Utils libs
import os
import json
import shutil
import numpy as np
import pandas as pd

from {{package_name}} import utils
from {{package_name}}.models_training.model_tfidf_cos import ModelTfidfCos
from {{package_name}}.models_training.utils_super_documents import TfidfVectorizerSuperDocuments
from sklearn.feature_extraction.text import TfidfVectorizer

# Disable logging
import logging
logging.disable(logging.CRITICAL)


def remove_dir(path):
    if os.path.isdir(path): shutil.rmtree(path)


class ModelTfidfCosTests(unittest.TestCase):
    '''Main class to test model_tfidf_cos'''

    def setUp(self):
        '''SetUp fonction'''
        # Change directory to script directory
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def test01_model_tfidf_cos_init(self):
        '''Test de tfidfDemo.models_training.model_tfidf_cos.ModelTfidfCos.__init__'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Init., test all params
        model = ModelTfidfCos(model_dir=model_dir)
        self.assertEqual(model.model_dir, model_dir)
        self.assertTrue(os.path.isdir(model_dir))
        self.assertFalse(model.pipeline is None)
        self.assertTrue(type(model.with_super_documents) == bool)
        # We test display_if_gpu_activated and _is_gpu_activated just by calling them
        self.assertTrue(type(model._is_gpu_activated()) == bool)
        model.display_if_gpu_activated()
        remove_dir(model_dir)

        # Check TFIDF params
        model = ModelTfidfCos(model_dir=model_dir, tfidf_params={'norm': 'l1', 'sublinear_tf': True})
        self.assertEqual(model.pipeline['tfidf'].norm, 'l1')
        self.assertEqual(model.pipeline['tfidf'].sublinear_tf, True)
        remove_dir(model_dir)

        # Check with super documents
        model = ModelTfidfCos(model_dir=model_dir, with_super_documents=True)
        self.assertEqual(model.with_super_documents, True)
        remove_dir(model_dir)

        # Error
        with self.assertRaises(ValueError):
            model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy='toto')
        remove_dir(model_dir)

        with self.assertRaises(ValueError):
            model = ModelTfidfCos(model_dir=model_dir, multi_label=True, with_super_documents=True)
        remove_dir(model_dir)


    def test02_model_tfidf_cos_fit(self):
        '''Test of the method fit of tfidfDemo.models_training.model_tfidf_cos.ModelTfidfCos'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Set vars
        x_train = np.array(["ceci est un test", "pas cela", "cela non plus", "ici test", "là, rien!"])
        y_train_mono = np.array([0, 1, 0, 1, 2])
        model_vec = TfidfVectorizer()

        # Without super documents
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=False)
        model.fit(x_train, y_train_mono)
        model_vec.fit(x_train, y_train_mono)
        self.assertEqual(model.tfidf.classes_, [0, 1, 2])
        self.assertEqual(model.matrix_train.toarray().all(), model_vec.fit_transform(x_train).toarray().all())
        self.assertEqual(model.array_target.all(), np.array(y_train_mono).all())
        remove_dir(model_dir)

        # With super documents
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=True)
        model.fit(x_train, y_train_mono)
        model_vec.fit(x_train, y_train_mono)

        self.assertEqual(model.tfidf.classes_, [0, 1, 2])
        self.assertEqual(model.matrix_train.toarray().shape[0], 5)
        self.assertEqual(model.array_target.all(), np.array(y_train_mono).all())
        remove_dir(model_dir)


    def test03_model_tfidf_cos_predict(self):
        '''Test of the method predict of tfidfDemo.models_training.model_tfidf_cos.ModelTfidfCos'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Set vars
        x_train = np.array(["ceci est un test", "pas cela", "cela non plus", "ici test", "là, rien!"])
        x_train_super_documents = np.array(["ceci est un test cela non plus", "pas cela ici test", "là, rien!"])
        y_train_mono = np.array([0, 1, 0, 1, 2])
        y_train_str = np.array(['a', 'b', 'a', 'b', 'c'])

        # Mono label - no strategy - with super documents
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=True)
        model.fit(x_train, y_train_mono)
        preds = model.predict('test', return_proba=False)
        self.assertEqual(preds, model.predict(['test'], return_proba=False)[0])
        remove_dir(model_dir)

        model_str = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=True)
        model_str.fit(x_train, y_train_str)
        preds_str = model_str.predict(x_train, return_proba=False)
        self.assertEqual(preds_str.shape, (len(x_train),))
        self.assertTrue((preds_str == y_train_str).all())
        remove_dir(model_dir)

        # Mono label - no strategy - without super documents
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=False)
        model.fit(x_train, y_train_mono)
        preds = model.predict(x_train, return_proba=False)
        self.assertEqual(preds.shape, (len(x_train),))
        preds = model.predict('test', return_proba=False)
        self.assertEqual(preds, model.predict(['test'], return_proba=False)[0])
        remove_dir(model_dir)

        # Model needs to be fitted
        with self.assertRaises(AttributeError):
            model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None)
            model.predict_proba('test')
        remove_dir(model_dir)

        with self.assertRaises(ValueError):
            model = ModelTfidfCos(model_dir=model_dir)
            model.fit(x_train, y_train_mono)
            model.predict('test',  return_proba=True)
        remove_dir(model_dir)

    def test04_model_tfidf_cos_save(self):
        '''Test of the method save of tfidfDemo.models_training.model_pipeline.ModelPipeline'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Nominal case
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None)
        model.save(json_data={'test': 8})
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, 'configurations.json')))
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, f"{model.model_name}.pkl")))
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, f"sklearn_pipeline_standalone.pkl")))
        with open(os.path.join(model.model_dir, 'configurations.json'), 'r', encoding='utf-8') as f:
            configs = json.load(f)
        self.assertEqual(configs['test'], 8)
        self.assertTrue('package_version' in configs.keys())
        self.assertEqual(configs['package_version'], utils.get_package_version())
        self.assertTrue('model_name' in configs.keys())
        self.assertTrue('model_dir' in configs.keys())
        self.assertTrue('trained' in configs.keys())
        self.assertTrue('nb_fit' in configs.keys())
        self.assertTrue('list_classes' in configs.keys())
        self.assertTrue('dict_classes' in configs.keys())
        self.assertTrue('x_col' in configs.keys())
        self.assertTrue('y_col' in configs.keys())
        self.assertTrue('multi_label' in configs.keys())
        self.assertTrue('level_save' in configs.keys())
        self.assertTrue('librairie' in configs.keys())
        self.assertEqual(configs['librairie'], 'scikit-learn')
        self.assertEqual(configs['multiclass_strategy'], None)
        # Specific model used
        self.assertTrue('tfidf_confs' in configs.keys())
        remove_dir(model_dir)


    def test05_model_tfidf_cos_reload_from_standalone(self):
        '''Test of the method tfidfDemo.models_training.model_tfidf_cos.ModelTfidfCos.reload'''

        ############################################
        # mono_label & without multi-classes strategy
        ############################################

        # Create model
        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        x_train = np.array(["ceci est un test", "pas cela", "cela non plus", "ici test", "là, rien!"])
        x_test = np.array(["ceci est un coucou", "pas lui", "lui non plus", "ici coucou", "là, rien!"])
        y_train_mono = np.array(['non', 'oui', 'non', 'oui', 'non'])
        model = ModelTfidfCos(model_dir=model_dir, multi_label=False, multiclass_strategy=None, with_super_documents=True)
        tfidf = model.tfidf
        model.fit(x_train, y_train_mono)
        model.save()

        # Reload
        pkl_path = os.path.join(model.model_dir, f"sklearn_pipeline_standalone.pkl")
        conf_path = os.path.join(model.model_dir, "configurations.json")
        matrix_train_path = os.path.join(model.model_dir, "matrix_train.csv")
        array_target_path = os.path.join(model.model_dir, "array_target.csv")
        new_model = ModelTfidfCos()
        new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path=pkl_path, matrix_train_path=matrix_train_path, array_target_path=array_target_path)

        # Test
        self.assertEqual(model.model_name, new_model.model_name)
        self.assertEqual(model.trained, new_model.trained)
        self.assertEqual(model.nb_fit, new_model.nb_fit)
        self.assertEqual(model.x_col, new_model.x_col)
        self.assertEqual(model.y_col, new_model.y_col)
        self.assertEqual(model.list_classes, new_model.list_classes)
        self.assertEqual(model.dict_classes, new_model.dict_classes)
        self.assertEqual(model.multi_label, new_model.multi_label)
        self.assertEqual(model.level_save, new_model.level_save)
        self.assertEqual(model.multiclass_strategy, new_model.multiclass_strategy)
        self.assertEqual(model.tfidf.get_params(), new_model.tfidf.get_params())
        self.assertEqual(model.with_super_documents, new_model.with_super_documents)
        self.assertEqual(model.tfidf.classes_, new_model.tfidf.classes_)
        self.assertEqual(model.matrix_train.toarray().all(), new_model.matrix_train.toarray().all())
        # We can't really test the pipeline so we test predictions
        self.assertTrue(len(np.setdiff1d(model.predict(x_test), new_model.predict(x_test))) == 0)
        self.assertTrue(len(np.setdiff1d(model.array_target, new_model.array_target)) == 0)
        remove_dir(model_dir)
        remove_dir(new_model.model_dir)

        ############################################
        # Errors
        ############################################

        with self.assertRaises(FileNotFoundError):
            new_model = ModelTfidfCos()
            new_model.reload_from_standalone(configuration_path='toto.json', sklearn_pipeline_path=pkl_path, matrix_train_path=matrix_train_path, array_target_path=array_target_path)
        with self.assertRaises(FileNotFoundError):
            new_model = ModelTfidfCos()
            new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path='toto.pkl', matrix_train_path=matrix_train_path, array_target_path=array_target_path)
        with self.assertRaises(FileNotFoundError):
            new_model = ModelTfidfCos()
            new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path=pkl_path, matrix_train_path='toto.csv', array_target_path=array_target_path)
        with self.assertRaises(FileNotFoundError):
            new_model = ModelTfidfCos()
            new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path=pkl_path, matrix_train_path=matrix_train_path, array_target_path='toto.csv')


    def test06_model_tfidf_cos_with_super_documents(self):
        '''Test of the fit and predict with super documents of tfidfDemo.models_training.model_tfidf_cos.ModelTfidfCos'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        corpus = np.array([
                        "Covid - Omicron : l'Europe veut prolonger le certificat Covid jusqu'en 2023",
                        "Covid - le point sur des chiffres qui s'envolent en France",
                        "Carte des résultats des législatives : les qualifiés circonscription par circonscription",
                            ])
        target = np.array(['s','s','p'])

        model = ModelTfidfCos(model_dir=model_dir)
        model_s = ModelTfidfCos(model_dir=model_dir, with_super_documents=True)
        model.fit(corpus, target)
        model_s.fit(corpus, target)
        preds = model_s.predict(corpus, return_proba=False)
        self.assertFalse(isinstance(model.tfidf, TfidfVectorizerSuperDocuments))
        self.assertTrue(isinstance(model_s.tfidf, TfidfVectorizerSuperDocuments))
        self.assertFalse(np.equal(model.tfidf.transform(corpus).toarray(), model_s.tfidf.transform(corpus).toarray()).all())
        self.assertEqual(preds.shape, (len(target),))
        remove_dir(model_dir)


# Perform tests
if __name__ == '__main__':
    # Start tests
    unittest.main()
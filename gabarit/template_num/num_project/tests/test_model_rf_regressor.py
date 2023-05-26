#!/usr/bin/env python3
# Copyright (C) <2018-2021>  <Agence Data Services, DSI Pôle Emploi>
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
from {{package_name}}.models_training.regressors.models_sklearn.model_rf_regressor import ModelRFRegressor
from sklearn.tree import DecisionTreeClassifier

# Disable logging
import logging
logging.disable(logging.CRITICAL)


def remove_dir(path):
    if os.path.isdir(path): shutil.rmtree(path)

def compare_trees(tree1: DecisionTreeClassifier, tree2: DecisionTreeClassifier) -> bool:
    '''Checks if two DecisionTreeClassifiers are equal
    Args:
        tree1 (DecisionTreeClassifier): First tree to consider
        tree2 (DecisionTreeClassifier): Second tree to consider
    Results:
        bool: True if all trees nodes and values are equal, else False
    '''
    state1 = tree1.tree_.__getstate__()
    state2 = tree2.tree_.__getstate__()
    if not np.array_equal(state1["nodes"], state2["nodes"]):
        return False
    if not np.array_equal(state1["values"], state2["values"]):
        return False
    return True   

class ModelRFRegressorTests(unittest.TestCase):
    '''Main class to test model_rf_regressor'''

    def setUp(self):
        '''SetUp fonction'''
        # Change directory to script directory
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def test01_model_rf_regressor_init(self):
        '''Test of the initialization of {{package_name}}.models_training.model_rf_regressor.ModelRFRegressor'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Init., test all parameters
        model = ModelRFRegressor(model_dir=model_dir)
        self.assertEqual(model.model_dir, model_dir)
        self.assertTrue(os.path.isdir(model_dir))
        self.assertTrue(model.pipeline is not None)
        self.assertEqual(model.model_type, 'regressor')
        self.assertEqual(model.random_seed, None)
        # We test display_if_gpu_activated and _is_gpu_activated just by calling them
        self.assertTrue(type(model._is_gpu_activated()) == bool)
        model.display_if_gpu_activated()
        remove_dir(model_dir)

        # Check RF parameters
        model = ModelRFRegressor(model_dir=model_dir, rf_params={'n_estimators': 51, 'max_depth': 6}, random_seed=42)
        self.assertEqual(model.pipeline['rf'].n_estimators, 51)
        self.assertEqual(model.pipeline['rf'].max_depth, 6)
        self.assertEqual(model.random_seed, 42)
        remove_dir(model_dir)

    def test02_model_rf_regressor_predict(self):
        '''Test of the method predict of {{package_name}}.models_training.model_rf_regressor.ModelRFRegressor'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Set vars
        x_train = pd.DataFrame({'col_1': [-5, -1, 0, -2, 2, -6, 3] * 10, 'col_2': [2, -1, -8, 2, 3, 12, 2] * 10})
        x_train_inv = pd.DataFrame({'col_2': [2, -1, -8, 2, 3, 12, 2] * 10, 'fake_col': [0.5, -3, 5, 5, 2, 0, 8] * 10, 'col_1': [-5, -1, 0, -2, 2, -6, 3] * 10})
        y_train_regressor = pd.Series([-3, -2, -8, 0, 5, 6, 5] * 10)
        x_col = ['col_1', 'col_2']
        y_col_mono = ['toto']

        # Regressor
        model = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir)
        model.fit(x_train, y_train_regressor)
        preds = model.predict(x_train, return_proba=False)
        self.assertEqual(preds.shape, (len(x_train),))
        with self.assertRaises(ValueError):
            probas = model.predict(x_train, return_proba=True)
        # Test inversed columns order
        preds_inv = model.predict(x_train_inv, return_proba=False)
        np.testing.assert_almost_equal(preds, preds_inv, decimal=5)
        remove_dir(model_dir)

        # Model needs to be fitted
        with self.assertRaises(AttributeError):
            model = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir)
            model.predict(pd.Series([-2, 3]))
        remove_dir(model_dir)

    def test03_model_rf_regressor_save(self):
        '''Test of the method save of {{package_name}}.models_training.model_rf_regressor.ModelRFRegressor'''
        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)

        # Nominal case
        model = ModelRFRegressor(model_dir=model_dir)
        model.save(json_data={'test': 8})
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, 'configurations.json')))
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, f"{model.model_name}.pkl")))
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, f"sklearn_pipeline_standalone.pkl")))
        self.assertTrue(os.path.exists(os.path.join(model.model_dir, 'preprocess_pipeline.pkl')))
        with open(os.path.join(model.model_dir, 'configurations.json'), 'r', encoding='{{default_encoding}}') as f:
            configs = json.load(f)
        self.assertEqual(configs['test'], 8)
        self.assertTrue('maintainers' in configs.keys())
        self.assertTrue('date' in configs.keys())
        self.assertTrue('package_version' in configs.keys())
        self.assertEqual(configs['package_version'], utils.get_package_version())
        self.assertTrue('model_name' in configs.keys())
        self.assertTrue('model_dir' in configs.keys())
        self.assertTrue('model_type' in configs.keys())
        self.assertEqual(configs['model_type'], 'regressor')
        self.assertTrue('trained' in configs.keys())
        self.assertTrue('nb_fit' in configs.keys())
        self.assertTrue('x_col' in configs.keys())
        self.assertTrue('y_col' in configs.keys())
        self.assertTrue('columns_in' in configs.keys())
        self.assertTrue('mandatory_columns' in configs.keys())
        self.assertTrue('level_save' in configs.keys())
        self.assertTrue('librairie' in configs.keys())
        self.assertEqual(configs['librairie'], 'scikit-learn')
        # Specific model used
        self.assertTrue('rf_confs' in configs.keys())
        remove_dir(model_dir)

    def test04_model_rf_regressor_reload_from_standalone(self):
        '''Test of the method {{package_name}}.models_training.regressors.models_sklearn.model_rf_regressor.ModelRFRegressor.reload_from_standalone'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        model_dir_2 = os.path.join(os.getcwd(), 'model_test_123456789_2')
        remove_dir(model_dir)

        # Set vars
        x_train = pd.DataFrame({'col_1': [-5, -1, 0, -2, 2, -6, 3] * 10, 'col_2': [2, -1, -8, 2, 3, 12, 2] * 10})
        y_train_regressor = pd.Series([-3, -2, -8, 0, 5, 6, 5] * 10)
        x_col = ['col_1', 'col_2']
        y_col_mono = ['toto']

        ############################################
        # Regression
        ############################################

        # Create model
        model = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir)
        rf = model.rf
        model.fit(x_train, y_train_regressor)
        model.save()
        # Reload
        pkl_path = os.path.join(model.model_dir, f"sklearn_pipeline_standalone.pkl")
        conf_path = os.path.join(model.model_dir, "configurations.json")
        preprocess_pipeline_path = os.path.join(model.model_dir, "preprocess_pipeline.pkl")
        new_model = ModelRFRegressor(model_dir=model_dir_2)
        self.assertTrue(new_model.preprocess_pipeline is None)
        new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path=pkl_path,
                                         preprocess_pipeline_path=preprocess_pipeline_path)
        # Tests
        self.assertEqual(model.model_name, new_model.model_name)
        self.assertEqual(model.model_type, new_model.model_type)
        self.assertEqual(model.trained, new_model.trained)
        self.assertEqual(model.nb_fit, new_model.nb_fit)
        self.assertEqual(model.x_col, new_model.x_col)
        self.assertEqual(model.y_col, new_model.y_col)
        self.assertEqual(model.columns_in, new_model.columns_in)
        self.assertEqual(model.mandatory_columns, new_model.mandatory_columns)
        self.assertEqual(model.level_save, new_model.level_save)
        self.assertEqual(model.rf.get_params(), rf.get_params())
        self.assertTrue(new_model.preprocess_pipeline is not None)
        # We can't really test the pipeline so we test predictions
        self.assertEqual([[_] for _ in model.predict(x_train)], [[_] for _ in new_model.predict(x_train)])
        remove_dir(new_model.model_dir)
        # We do not remove model_dir to test the errors

        ############################################
        # Errors
        ############################################

        with self.assertRaises(FileNotFoundError):
            new_model = ModelRFRegressor(model_dir=model_dir_2)
            new_model.reload_from_standalone(configuration_path='toto.json', sklearn_pipeline_path=pkl_path,
                                             preprocess_pipeline_path=preprocess_pipeline_path)
        with self.assertRaises(FileNotFoundError):
            new_model = ModelRFRegressor(model_dir=model_dir_2)
            new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path='toto.pkl',
                                             preprocess_pipeline_path=preprocess_pipeline_path)
        with self.assertRaises(FileNotFoundError):
            new_model = ModelRFRegressor(model_dir=model_dir_2)
            new_model.reload_from_standalone(configuration_path=conf_path, sklearn_pipeline_path=pkl_path,
                                             preprocess_pipeline_path='toto.pkl')

        # Clean
        remove_dir(model_dir)

    def test05_model_rf_classifier_fit_with_seed(self):
        '''Test random seed for {{package_name}}.models_training.regressors.models_sklearn.model_rf_regressor.ModelRClassifier'''

        model_dir = os.path.join(os.getcwd(), 'model_test_123456789')
        remove_dir(model_dir)
        model_dir2 = os.path.join(os.getcwd(), 'model_test_1234567892')
        remove_dir(model_dir2)

        x_train = pd.DataFrame({'col_1': [-5, -1, 0, -2, 2, -6, 3] * 10, 'col_2': [2, -1, -8, 2, 3, 12, 2] * 10})
        y_train_regressor = pd.Series([-3, -2, -8, 0, 5, 6, 5] * 10)
        x_col = ['col_1', 'col_2']
        y_col_mono = ['toto']

        # Regression with same random_seed
        model1 = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir, random_seed=42)
        model1.fit(x_train, y_train_regressor)
        model2 = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir2, random_seed=42)
        model2.fit(x_train, y_train_regressor)
        self.assertEqual(model1.rf.get_params(),  model2.rf.get_params())
        # Checks if both models subtrees are equal
        self.assertTrue(all(compare_trees(tree1, tree2) for tree1, tree2 in zip(model1.rf.estimators_, model2.rf.estimators_)))
        remove_dir(model_dir), remove_dir(model_dir2)

        # Regression with different random_seed
        model1 = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir, random_seed=42)
        model1.fit(x_train, y_train_regressor)
        model2 = ModelRFRegressor(x_col=x_col, y_col=y_col_mono, model_dir=model_dir2, random_seed=41)
        model2.fit(x_train, y_train_regressor)
        self.assertNotEqual(model1.rf.get_params(),  model2.rf.get_params())
        # Checks if both models subtrees are equal
        self.assertFalse(all(compare_trees(tree1, tree2) for tree1, tree2 in zip(model1.rf.estimators_, model2.rf.estimators_)))
        remove_dir(model_dir), remove_dir(model_dir2)


# Perform tests
if __name__ == '__main__':
    # Start tests
    unittest.main()

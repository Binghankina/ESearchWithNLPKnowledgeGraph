
This code trains a word to vec embedding model, which can be used to find words appear in the same/similar context.


### How to set up? ###

clone this repo. 

Install tensorflow and sklearn from pip. 

'word_2_vec.py' is the program entry.

The functions in the main of 'word_2_vec.py' is the minimum example to train the model and serve using the model.

you will need to have a ./embedding folder created to save the snapshots of the model during training

The essential steps and functions are explained below:

1. the input data should be correctly setup in the variable 'filename', a small test dataset 'test_data_small.csv' is included in the repo

2. data is loaded with multiple reader threads using function multi_thread_read(filename)

3. the function assigns global variable 'data'

4. we use subsampling to increase the accuracy of the model: sub_vocabulary = subsampling(vocabulary)

5. the dataset is built using this function 'data, count, dictionary, reverse_dictionary = build_dataset(sub_vocabulary, vocabulary_size)', 

6. essentially, 'build_dataset' constructs word pairs that occur in the same context. the context length can be set using vairable 'skip_window'

7. when we have the 'word pairs', we can train them using 'train(data, reverse_dictionary, continue_train)'

8. during training, the model is preserved every 20 000 steps in './embedding/embedding' and './embedding/dictionary'. the loss during the training is output every 2000 steps.

9. the number of training steps can be specified in variable 'num_training_steps'

10. in order to speed up the training, you may want to have a larger learning rate at the begining and smaller learning rate later on. the learning rate can be set in variable 'learning_rate'

11. the model can be training with a learning rate for a number of steps and then the model is preserved. then you can use the preserved model to continue training the model using a lower learning rate. the flag to continue training is 'continue_train'

12. if you want to train based on the same dataset we just built, it is saved in 'data.pickle', if you want to continue using it without loading it again (takes lots of time), rename 'data.pickle' to 'data_current.pickle' and the program will find it.

13. after you are satisfied with the loss, our model is trained, so we have these two files './embedding/embedding' and './embedding/dictionary'. 

14. in order to use the trained model, we first load them in memory 'final_embeddings, reverse_dictionary = load_embedding('./embedding/embedding', './embedding/dictionary')'

15. then we pass them to 'serve("公债",final_embeddings,reverse_dictionary)', for example, you want to find similar words to '公债' 


'''
Author:     Tan Hao Hao
Project:    deeppop
Purpose:    Train and generate chord sequence from chord sequence dataset.
'''

import random

import numpy as np
from keras.layers import TimeDistributed, Embedding, Bidirectional, LSTM
from music21 import *
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.utils.np_utils import to_categorical
from keras import backend as K
from keras.models import load_model
import os


# Configurable variables
CHORD_SEQUENCE_FILE = "../chord/chord_sequence_all_no_repeat.txt"
CHORD_SEQUENCE_FILE_SHIFTED = "../chord/chord_sequence_all_no_repeat_normalized.txt"
TT_SPLIT = 0.8  # percentage of train / test
CHORD_DICT = {
  "Cb": 12, "C": 1, "C#": 2, "Db": 2, "D": 3, "D#": 4, "Eb": 4, "E": 5, "E#": 6,
  "Fb": 5, "F": 6, "F#": 7, "Gb": 7, "G": 8, "G#": 9, "Ab": 9, "A": 10, "A#": 11, 
  "Bb": 11, "B": 12, "B#": 1
}
DECODE_DICT = {
  1: "C", 2: "C#", 3: "D", 4: "D#", 5: "E", 6: "F", 7: "F#", 8: "G", 9: "G#", 10: "A", 11: "A#", 12: "B"
}
MAJ, MIN = ["maj", "min"]   # major is even and minor is +1 odd. Hence Cmaj=2, Cmin=3, C#maj=4 and etc.
TIME_FRAME = 8              # 8 notes timeframe, train by sliding window
NUM_CLASSES = 26            # 2-25 for major and minor, 0 for None, 1 is not used
EPOCH_NUM = 5               # number of epochs for training

MODEL_NAME = 'bidem'       # model is either normal vanilla RNN, or bidem


class ChordGenerator:
    def __init__(self, filename=CHORD_SEQUENCE_FILE_SHIFTED):
        self.train_file = filename

    def preprocess_data(self, tt_split = 0.9, is_small_dataset=True):
        '''
        Preprocess data.
        :param tt_split: train test split percentage
        :return: X_train, X_test, Y_train, Y_test
        '''
        filename = self.train_file
        chord_sequences = [a.rstrip() for a in open(filename, 'r+').readlines()]
        random.shuffle(chord_sequences)
        if is_small_dataset:
            chord_sequences = chord_sequences[:2000]

        # len_list = [len(k.split(' > ')) for k in chord_sequences]
        # plt.hist(len_list, normed=True, bins=10)
        # from this histogram, median is 50. take 50 as max.
        # plt.show()

        max_len = 50
        chords_processed = np.zeros((len(chord_sequences), max_len))

        for i in range(len(chord_sequences)):
            sequence = chord_sequences[i]
            chords = sequence.split(' > ')
            chords = chords[:] if len(chords) <= max_len else chords[:max_len]
            for j in range(len(chords)):
                chords_processed[i][j] = self.chord_to_id(chords[j])

        # pad chords_processed with TIME_FRAME - 1 zeros, so we can generate
        # starting with chords lesser than TIME_FRAME
        chords_processed = np.pad(chords_processed, ((0,0), (7,0)), 'constant', constant_values=0)

        # print(chord_sequences[12])
        # print(chords_processed[12])

        # same strategy as rhythm generator, but tf=8, many-to-one
        chords_in_tf = []
        for i in range(len(chords_processed)):
            cur_chords, cur_chords_len = chords_processed[i], len(chords_processed[i])
            for j in range(cur_chords_len - TIME_FRAME):
                chords_in_tf.append([cur_chords[j : j + TIME_FRAME + 1]])

        chords_in_tf = np.squeeze(np.asarray(chords_in_tf))
        X, Y = chords_in_tf[:, :-1], chords_in_tf[:, -1]
        X_oh, Y_oh = to_categorical(X, num_classes=NUM_CLASSES), to_categorical(Y, num_classes=NUM_CLASSES)

        tt_split_index = int(tt_split * len(chords_in_tf))
        X_train, X_test, Y_train, Y_test = X_oh[:tt_split_index], X_oh[tt_split_index:], \
                                           Y_oh[:tt_split_index],Y_oh[tt_split_index:]

        # print("X_train.shape: {}, Y_train.shape: {}".format(X_train.shape, Y_train.shape))
        # print("X_test.shape:{} , Y_test.shape: {}".format(X_test.shape, Y_test.shape))
        return X_train, X_test, Y_train, Y_test

    def build_model_architecture(self, num_seq, num_dim):
        model = Sequential()
        model.add(LSTM(64, return_sequences=True, input_shape=(num_seq, num_dim)))
        model.add(Dropout(0.2))
        model.add(Activation('relu'))
        model.add(LSTM(128, return_sequences=False))
        model.add(Dense(num_dim))
        model.add(Activation('softmax'))

        return model

    def build_model(self):
        '''
        Build the neural network model.
        :param X_test
        :param Y_train
        :param Y_test
        :return: model
        '''
        num_seq = 8

        model = Sequential()
        model.add(Embedding(NUM_CLASSES, 32, input_shape=(num_seq,)))     # NUM_CLASSES is the total number of chord IDs
        model.add(Bidirectional(LSTM(64, return_sequences=True)))
        model.add(Activation('tanh'))
        model.add(Bidirectional(LSTM(128, return_sequences=False)))
        model.add(Dense(NUM_CLASSES))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def train_model(self, model, X_train, Y_train, X_test, Y_test):
        model.summary()
        history = model.fit(X_train, Y_train, epochs=EPOCH_NUM)
        scores = model.evaluate(X_train, Y_train, verbose=True)
        print('Train loss:', scores[0])
        print('Train accuracy:', scores[1])
        scores = model.evaluate(X_test, Y_test, verbose=True)
        print('Test loss:', scores[0])
        print('Test accuracy:', scores[1])

        # plt.plot(range(len(history.history['loss'])), history.history['loss'], label='train loss')
        # plt.savefig('training_graph.png')
        return model

    def __generate_chord_from_seed(self, example_chord, model, num_of_chords=32, is_one_hot=False):
        '''
        Private method to generate chords given a seed sequence of chords
        :param example_chord:
                A seed sequence of chords of any length to kick start the generation.
        :param model:
                Model used to generate the chords.
        :param num_of_chords:
                Number of chords needed for generation.
        :return:
                chord sequence generated
        '''
        seed_chord = example_chord[:]    # seed beat pattern for generation
        # print('seed chord', seed_chord)
        result_chord = seed_chord[:]
        index = 0

        while len(result_chord) < num_of_chords:
            # terminating condition now only consist of a fixed length
            cur_chord_block = result_chord[index : index + TIME_FRAME]
            next_chord = self.__generate_next_chord(cur_chord_block, model, is_one_hot=is_one_hot)
            result_chord.append(next_chord)
            index += 1

        while result_chord[0] == '-':
            cur_chord_block = result_chord[len(result_chord) - TIME_FRAME:]
            next_chord = self.__generate_next_chord(cur_chord_block, model, is_one_hot=is_one_hot)
            result_chord.append(next_chord)
            result_chord.pop(0)

        return result_chord

    def __generate_next_chord(self, chord_block, model, is_one_hot=False):
        '''
        Private method to generate next chord given a chord block.
        :param chord_block:
        :param model:
        :return: next chord
        '''
        predict_chord_oh = self.one_hot_encode_chords(chord_block, is_one_hot=is_one_hot)
        predict_chord_oh = np.expand_dims(predict_chord_oh, axis=0)

        # prediction = model.predict_classes(predict_chord_oh)
        prediction_proba = model.predict(predict_chord_oh)
        prediction_random_sample = np.random.choice(NUM_CLASSES, 1, p=prediction_proba.flatten())[0]

        # for now, use finite number - if i want 40 chords, should have 40 chords
        while prediction_random_sample == 0:
            prediction_random_sample = np.random.choice(NUM_CLASSES, 1, p=prediction_proba.flatten())[0]

        result = self.id_to_chord(prediction_random_sample)      # random sampling
        return result

    def chords_to_midi(self, chords, name='chords_to_midi.mid', is_chord=True,
                       add_rest=False, chord_duration=4):
        '''

        :param chords:
        :param name:
        :param is_chord:
            If is_chord is True, generate chords midi; else, generate note bassline midi
        :return:
        '''
        s = stream.Stream()
        for c in chords:
            if c == '-':
                if add_rest:
                    r = note.Rest()
                    r.duration.quarterLength = 1 / 12
                    s.append(r)       # add a rest of quarter note length
                continue
            note_name, quality = c.split(':')
            note_value = CHORD_DICT[note_name]

            # generate chords midi
            if is_chord:
                if quality == 'maj':
                    value_lst = [note_value, (note_value + 4) % 12, (note_value + 7) % 12]
                else:
                    value_lst = [note_value, (note_value + 3) % 12, (note_value + 7) % 12]

                for i in range(len(value_lst)):
                    if value_lst[i] == 0:
                        value_lst[i] = 12

                if value_lst[1] > value_lst[0]:
                    if value_lst[2] > value_lst[1]:
                        octave_lst = [3,3,3]
                    else:
                        octave_lst = [3,3,4]
                else:
                    octave_lst = [2,3,3]

                new_value_lst = []
                for i in range(len(value_lst)):
                    new_value_lst.append(DECODE_DICT[value_lst[i]] + str(octave_lst[i]))
                d = duration.Duration(chord_duration)    # whole note length
                temp_chord = chord.Chord(new_value_lst, duration=d)
                s.append(temp_chord)

            # generate bass note midi
            else:
                bass_note = note.Note(note_name + '1')
                s.append(bass_note)

        fp = name
        s.write('midi', fp=fp)
        return fp

    def one_hot_encode_chords(self, chord_block, is_one_hot=True):
        '''
        Helper function to encode chord block to one-hot matrix.
        :return: one-hot martix of chord
        '''
        if isinstance(chord_block, str):
            chord_block = chord_block.split(' > ')
        encoded_chord_pattern = np.zeros((len(chord_block)))
        for i in range(len(chord_block)):
            encoded_chord_pattern[i] = self.chord_to_id(chord_block[i])
        if is_one_hot:
            return to_categorical(encoded_chord_pattern, num_classes=NUM_CLASSES)
        else:
            return encoded_chord_pattern

    def decode_chords_from_one_hot(self, one_hot_beats):
        return ''.join([DECODE_DICT[encode] for encode in one_hot_beats.flatten()])

    # change chord of format <name>:<tonality> to id between 2-25
    def chord_to_id(self, chord):
        if ':' not in chord:
            return 0
        chord_name, chord_tonality = chord.split(':')
        chord_id = CHORD_DICT[chord_name] * 2           # leave 0 for empty chords
        if MIN in chord_tonality:
            chord_id += 1                               # odd number for minors
        return chord_id

    def id_to_chord(self, idnum):
        if idnum == 0:
            return "-"
        elif idnum % 2 == 0:
            return DECODE_DICT[idnum / 2] + ':' + MAJ
        else:
            return DECODE_DICT[(idnum - 1) / 2] + ':' + MIN

    def __normalize_to_c(self, chords):
        for ch in chords:
            if ch != '-':
                first_chord = ch
                break
        first_key, first_tonality = first_chord.split(':')
        first_key_index = CHORD_DICT[first_key]
        key_of_c = 1
        diff = first_key_index - key_of_c
        if diff > 0:
            for i in range(len(chords)):
                c = chords[i]
                if c != '-':
                    k, tonality = c.split(':')
                    key_index = CHORD_DICT[k]
                    transposed_key_index = key_index - diff
                    if transposed_key_index <= 0:
                        transposed_key_index += 12
                    transposed_key = DECODE_DICT[transposed_key_index]
                    chords[i] = ':'.join([transposed_key, tonality])
        return chords

    def __unnormalize_from_c(self, chords, first_key_original):
        for ch in chords:
            if ch != '-':
                first_chord = ch
                break
        first_key, first_tonality = first_chord.split(':')
        first_key_index = CHORD_DICT[first_key]
        key_of_original = CHORD_DICT[first_key_original]
        diff = key_of_original - first_key_index
        if diff > 0:
            for i in range(len(chords)):
                c = chords[i]
                if c != '-':
                    k, tonality = c.split(':')
                    key_index = CHORD_DICT[k]
                    transposed_key_index = key_index + diff
                    if transposed_key_index > 12:
                        transposed_key_index -= 12
                    transposed_key = DECODE_DICT[transposed_key_index]
                    chords[i] = ':'.join([transposed_key, tonality])
        return chords

    def load_model(self, X_train, X_test, Y_train, Y_test, is_retrain):
        # clear session to avoid any errors
        K.clear_session()

        if 'normalized' in self.train_file:
            if MODEL_NAME == 'bidem':
                chord_weights_file = '../chord/chord_weights_bidem.h5'
            else:
                chord_weights_file = '../chord/chord_weights_normalized-v1.h5'

            if os.path.exists(chord_weights_file) and not is_retrain:
                print('Loading ' + chord_weights_file + '...')
                if MODEL_NAME == 'bidem':
                    model = self.build_model()
                else:
                    model = self.build_model_architecture(X_train.shape[1], X_train.shape[2])
                model.load_weights(chord_weights_file)

            else:
                print('Training chord model...')
                model = self.build_model()
                model = self.train_model(model, X_train, X_test, Y_train, Y_test)
                model.save(chord_weights_file)

        else:
            if os.path.exists('../chord/chord_weights_unnormalized.h5') and not is_retrain:
                print('Loading chord_weights_unnormalized.h5...')
                model = self.build_model_architecture(X_train.shape[1], X_train.shape[2])
                model.load_weights('../chord/chord_weights_unnormalized.h5')
            else:
                model = self.build_model()
                model.save_weights('../chord/chord_weights_unnormalized.h5')

        return model

    def generate_chords(self, example_chord=None, num_of_chords=32, is_retrain=False):
        X_train, X_test, Y_train, Y_test = self.preprocess_data(TT_SPLIT, is_small_dataset=False)
        model = self.load_model(X_train, X_test, Y_train, Y_test, is_retrain=is_retrain)

        if not example_chord:
            # if no example chord sequence is provided, randomly generate one from train data
            index = random.randint(0, 100)
            example_chord = open(self.train_file).readlines()[index].split(' > ')
            example_chord = example_chord[:8]
            first_chord = example_chord[0].split(':')[0]

        else:
            # if given example chord sequence length < TIME_FRAME, pad with zeros
            for ch in example_chord:
                if ch != '-':
                    first_chord = ch
                    break
            first_chord = first_chord.split(':')[0]
            if len(example_chord) < TIME_FRAME:
                for i in range(TIME_FRAME - len(example_chord)):
                    example_chord.insert(0, '-')
            else:
                example_chord = example_chord[:TIME_FRAME]

        # if unnormalized, is_one_hot = True
        # if normalized, is not bidem, is_one_hot = True
        is_one_hot = ("normalized" not in self.train_file) or ("normalized" in self.train_file and MODEL_NAME != 'bidem')

        if 'normalized' in self.train_file:
            result_chord = self.__generate_chord_from_seed(self.__normalize_to_c(example_chord),
                                                           model,
                                                           num_of_chords,
                                                           is_one_hot=is_one_hot)

            result_chord = self.__unnormalize_from_c(result_chord, first_chord)

            open('example_chord.txt', 'w+').write(' > '.join(example_chord))
            open('result_chord.txt', 'w+').write(' > '.join(result_chord))

            return result_chord
        else:
            return self.__generate_chord_from_seed(example_chord, model, num_of_chords,
                                                   is_one_hot=is_one_hot)


if __name__ == "__main__":
    # chord_generator = ChordGenerator(CHORD_SEQUENCE_FILE)
    chord_generator = ChordGenerator()
    chord_generator.generate_chords(['D:maj', 'A:maj', 'B:min'])
    # result = chord_generator.generate_chords(['G:min', 'D:maj', 'Eb:maj'])
    # print(result)
    # chord_generator.evaluate_chord_variation_coefficient(result)
    # chord_generator.chords_to_midi(result)
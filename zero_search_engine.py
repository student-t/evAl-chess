from keras.models import load_model
import chess
import train
import extract_features
import numpy as np

model = load_model('/Users/colinni/evAl-chess/saved_keras_model_merged_first.h5')

def engine_evaluate(position):
    '''
    The zero-search engine's evaluation of `position`; a higher number means
    that the engine evaluates that the position favors white.
    '''
    print(type(position))
    x_unscaled = np.array([extract_features.get_features(position)]).astype(float)
    print(x_unscaled)
    x_scaled = train.scaler_X.transform(x_unscaled)
    y_scaled = scaled_evaluation = model.predict(extract_features.split_features(np.array(x_scaled)))
    y_unscaled = unscaled_evaluation = train.scaler_Y.inverse_transform(np.reshape(y_scaled, (len(y_scaled), 1)))
    return unscaled_evaluation


def get_engine_analysis(position):
    '''
    The result of the zero-search engine's mini-max search for each possible
    move. Of course for an engine that doesn't search, it's basically just
    the evaluation of the positions at depth 1.

    (Funnily enough, the engine can't differentiate between legal and
    illegal positions. So we're going to give it only legal moves to decide
    from. Heh, oops -- I thought I forgot to add something to the training
    data...)
    '''
    engine_analysis = { }
    for move in position.legal_moves:
        # Play the move; evaluate the position; then 'unplay' the move.
        position.push(move)
        eval_position = engine_evaluate(position)
        engine_analysis[move] = eval_position
        position.pop()

    return engine_analysis


def get_engine_move(position, playing_color):
    return (
        max(
            get_engine_analysis(position).items(),
            key=lambda item : item[1]
        )
        if playing_color == chess.WHITE
        else min(
            get_engine_analysis(position).items(),
            key=lambda item : item[1]
        )
    )

def alpha_beta(position, depth, alpha=-500, beta=+500, color=chess.WHITE):
    if depth == 0:
        return engine_evaluate(position)
    elif color == chess.WHITE:
        v = -500
        for move in position.legal_moves:
            position.push(move)
            v = max(v, alpha_beta(position, depth - 1, alpha, beta, chess.BLACK))
            alpha = max(alpha, v)
            if beta <= alpha:
                break
            position.pop()
        return v
    elif color == chess.BLACK:
        v = 500
        for move in position.legal_moves:
            position.push(move)
            v = min(v, alpha_beta(position, depth - 1, alpha, beta, chess.WHITE))
            beta = min(beta, v)
            if beta <= alpha:
                break
            position.pop()
        return v

def play_engine(verbose=False):
    position = chess.Board()

    while not position.is_game_over():
        engine_move, _eval = get_engine_move(position, chess.WHITE)
        engine_move, _eval = alpha_beta(position, 2)

        # if verbose:
        #     for move, _eval in get_engine_analysis(position).items():
        #         print(move, _eval)
        print('Engine played', engine_move)
        position.push(engine_move)
        print(position)
        print()
        player_move = input('Your move: ')
        position.push_san(player_move)



play_engine(True)
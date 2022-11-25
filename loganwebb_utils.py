import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def agg_statcast_pitchers(pitcher, min_batters_faced):
    """ 
    Takes a dataframe representing a pitcher's events and if he faced at least min_batters_faced then compute 
    putaway_rate and k_rate.
    
    pitcher [DataFrame]: Dataframe of events for pitcher.
    min_batters_faced [int]: if pitcher faced less than this number, return NaN
    
    Returns: a pandas Series object with the info.
    """
    appearances = len(pitcher[(pitcher['description'].isin(['hit_by_pitch','hit_into_play','hit_into_play_no_out',
     'hit_into_play_score'])) | (pitcher['events'].isin(['strikeout', 'walk']))])
    pitcher_2str = pitcher[pitcher['strikes']==2]
    if appearances < min_batters_faced:
        return pd.Series({'putaway_rate': float('NaN'), 'k_rate': float('NaN')})
    putaways = len(pitcher_2str[pitcher_2str['description'].isin(['swinging_strike','swinging_strike_blocked', 
                                                                     'called_strike'])])
    putaway_rate = putaways/len(pitcher_2str)
    strikeouts = len(pitcher[pitcher['events']=='strikeout'])
    k_rate = strikeouts/appearances
    return pd.Series({'putaway_rate': putaway_rate, 'k_rate': k_rate})


def parse_prop(row, df):
    """ Return proportion of each pitch. """
    return len(df[df['pitch_type']==row.name])/len(df)


def parse_xwoba(row):
    """ Calculate xwOBA. """
    if np.isnan(row.estimated_woba_using_speedangle):
        return row.woba_value
    else:
        return row.estimated_woba_using_speedangle
    
    
def release_point_analysis(df, pitches, year, webb=False):
    """ Given a dataframe representing a pitcher, return the release point variance for each pitch in pitches. """
    res = {}
    for pitch in pitches:
        res[pitch] = float('NaN')
        if webb and year == '2019' and pitch == 'SI':
            pitch = 'FT'
        if len(df[df['pitch_type']==pitch]) > 20:
            avg_x = df[df['pitch_type']==pitch]['release_pos_x'].sum()/len(
            df[df['pitch_type']==pitch])
            avg_z = df[df['pitch_type']==pitch]['release_pos_z'].sum()/len(
                df[df['pitch_type']==pitch])
            avg = np.array((avg_x, avg_z))
            rel = df[df['pitch_type']==pitch][['release_pos_x', 'release_pos_z']].values
            rel_dist = []
            for i in range(0, rel.shape[0]):
                rel_dist.append(np.linalg.norm(avg-rel[i]))
            stat = np.mean(rel_dist)
            if webb and year == '2019' and pitch == 'FT':
                pitch = 'SI'
            res[pitch]=stat
    return pd.Series(res)
    
    
def whiff_by_height(pitches, df, heights):
    """ Computes whiff rate/clean rate by height and plot. """
    
    # "universal" strike zone params
    lowerb = 18.29/12
    upperb = lowerb+(25.79/12)
    leftb = -9.97/12
    rightb = leftb +(19.94/12)
    
    for pitch in pitches:
        freqs = {}
        for height in heights:
            print('\nINFO FOR ' + str(pitch) + ' at ' + str(height))
            df_pitch = df[(df['pitch_type']==pitch) & (df['plate_z'] > height[0]) &
                         (df['plate_z'] <= height[1])]
            whiffs = df_pitch[df_pitch['description'].isin(['swinging_strike', 'swinging_strike_blocked'])]
            swings = df_pitch[df_pitch['description'].isin(['swinging_strike','swinging_strike_blocked',
                    'hit_into_play', 'hit_into_play_no_out', 'hit_into_play_score', 'foul_tip', 'foul', 'foul_bunt'])]
            if len(swings) > 0:
                whiff_rate = len(whiffs)/len(swings)
            else:
                whiff_rate = float('NaN')
            clean = len(df_pitch[df_pitch['description'].isin(['swinging_strike', 'swinging_strike_blocked', 
                                                               'called_strike'])])
            chances = len(df_pitch)
            if chances > 0:
                clean_rate = clean/chances
            else:
                clean_rate = float('NaN')
            called_str = len(df_pitch[df_pitch['description']=='called_strike'])
            strikes = len(df_pitch[(df_pitch['plate_z'] >= lowerb) & (df_pitch['plate_z'] <= upperb) &
                         (df_pitch['plate_x'] >= leftb) & (df_pitch['plate_x'] <= rightb)])
            print(pitch + ' clean rate: ' + str(clean_rate))
            print(pitch + ' whiff rate: ' + str(whiff_rate))
            print(pitch + ' whiffs: ' + str(len(whiffs)))
            print(pitch + ' called strikes: ' + str(called_str))
            print(pitch + ' swings: ' + str(len(swings)))
            print(pitch + ' strikes: ' + str(strikes))
            print(pitch + ' chances: ' + str(chances))
            freqs[height] = len(df_pitch)

            # plot
            ax = df_pitch.plot(x='plate_x', y='plate_z', kind='scatter')
            swings.plot(ax=ax, x='plate_x', y='plate_z', kind='scatter', color='purple')
            whiffs.plot(ax=ax, x='plate_x', y='plate_z', kind='scatter', color='orange')
            ax = plt.gca()
            rect = patches.Rectangle((-9.97/12,18.29/12),19.94/12,25.79/12,linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(rect)
            plt.xlim([-3, 3])
            plt.ylim([0, 6])
            plt.show()
        total = sum(freqs.values())
        for height in freqs:
            freqs[height] /= total
        print("frequencies for " + pitch + ' by height: ' + str(freqs))
        
    
    
    
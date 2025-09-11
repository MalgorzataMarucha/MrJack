import settings
import mechanics.deck as deck
import mechanics.actions as actions
import time
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import mechanics.map_switch as map_switch
import mechanics.map_utils as map_utils
from matplotlib.ticker import MaxNLocator
import gc
import tracemalloc
        
def full_reset():
    # usunięcie potencjalnych „ciężkich” struktur
    for attr in ["hex_map", "building_list", "character_list", "lamps_to_turn_off", "get_out_hex"]:
        if hasattr(settings, attr):
            setattr(settings, attr, None)
    gc.collect()
    settings.reset()

def run_simulation(option, type_of_measurement, use_random=False, measure_memory = False ):
    if measure_memory:
        memory_amount = []
        tracemalloc.start()
    settings.reset()
    print("------------------------------------------")
    print(settings.amount_of_rolls)
    if type_of_measurement != "operations":
        settings.operations = None
    deck.choose_murderer(settings.character_list)
    deck.create_suspect_list()
    map_utils.prepare_lanterns()
    if measure_memory:
        current, _ = tracemalloc.get_traced_memory()
        memory_amount.append(current)
    while not actions.finish_of_game(settings.round_number, settings.caught):
        if measure_memory:
            current, _ = tracemalloc.get_traced_memory()
            memory_amount.append(current)
            
        settings.already_used_skill = False
        settings.already_moved = False
        settings.round_number, move_info = deck.choose_char(settings.round_number)
        settings.move_stage = actions.time_to_execute_skill(move_info['player'], move_info['character'])
        if settings.operations:
            settings.operations += 2

        if settings.move_stage == 1:
            if measure_memory:
                current, _ = tracemalloc.get_traced_memory()
                memory_amount.append(current)
            gc.collect()
            settings.already_moved = True
            actions.execute_movement(move_info['player'], move_info['character'], use_random)
            settings.already_used_skill = True
            actions.using_characters(move_info['player'], move_info['character'], use_random)
            if settings.operations:
                settings.operations += 2

        else:
            if measure_memory:
                current, _ = tracemalloc.get_traced_memory()
                memory_amount.append(current)
            gc.collect()
            settings.already_used_skill = True
            actions.using_characters(move_info['player'], move_info['character'], use_random)
            settings.already_moved = True
            actions.execute_movement(move_info['player'], move_info['character'], use_random)
            if settings.operations:
                settings.operations += 2
            if not settings.already_used_skill:
                actions.using_characters(move_info['player'], move_info['character'], use_random)

        if settings.ready_for_next_round:
            settings.round_number += 1
            gc.collect()
            deck.is_Jack_visible()
            deck.update_suspect_list()
            settings.ready_for_next_round = False
            if settings.operations:
                settings.operations += 3

        if measure_memory:
            current, _ = tracemalloc.get_traced_memory()
            memory_amount.append(current)

        
    
    result = actions.finish_of_game(settings.round_number, settings.caught)
    if measure_memory:
        current, peak = tracemalloc.get_traced_memory()
        memory_amount.append(current)
        tracemalloc.stop()
        avg_memory = np.mean(memory_amount)
        return result, avg_memory, peak
    else:
        return result


def run_multiple_simulations(n=50, increase_of_rounds = 8, moves = 3, option=None, use_random=False):
    full_reset()
    settings.col_row_hex = settings.init_col_row_hex()
    if option != None:
        map_switch.increase_the_map(settings.col_row_hex, option)
        map_switch.prepare_the_map(option, settings.building_list, settings.character_list, settings.get_out_hex)
        map_switch.prepare_buildings(option, settings.building_list, settings.character_list, settings.get_out_hex, settings.hex_map)
        if option == 0:
            settings.max_rounds = 8
        else:
            settings.max_rounds += increase_of_rounds

        settings.amount_of_rolls = moves
        
    results_time = []
    results_operations = []
    results_memory = []
    results_max_memory = []
    type_of_finish = {"Detective caught Jack. Detective wins!" : 0,
                      "Jack managed to run away. Jack wins!": 0,
                      "Detective didn't manage to catch Jack in time. Jack wins!": 0}
    avg_time = 0
    avg_operations = 0
    avg_memory = 0
    avg_highest_memory = 0
    
    for type_of_measurement in ["memory"]:
        queue = 0
        for _ in range(n):
            queue += 1
            print(queue)
            if type_of_measurement == "time":
                start_time = time.time()
                finish = run_simulation(option, type_of_measurement, use_random)   
                elapsed_time = time.time() - start_time
                results_time.append((elapsed_time))
            elif type_of_measurement == "operations":
                finish = run_simulation(option, type_of_measurement, use_random)
                results_operations.append(int(settings.operations))
            else:
                
                finish, result, peak = run_simulation(option, type_of_measurement, use_random, measure_memory=True) 
                results_memory.append(result)
                results_max_memory.append(peak)

            if finish in type_of_finish:
                type_of_finish[finish] += 1
    avg_time = np.mean(results_time)
    avg_operations = np.mean(results_operations)
    avg_memory = np.mean(results_memory)
    avg_highest_memory = np.mean(results_max_memory)
    return avg_time, avg_operations, avg_memory, avg_highest_memory, type_of_finish

# ---------------- FITTING ---------------- #

def linear_func(x, m, c):
    return m*x + c

def log_func(x, a, c):
    return a*np.log2(x) + c*x

def linear_log(x, a, b):
    return a*x*np.log2(x) + b

def quadratic(x, a, b, c):
    return a*x**2 + b*x + c

def simulate_and_save(filename="simulation_summary.xlsx"):
    size_of_map = list(range(0, 41, 2))
    #increase_of_rounds = [0, 2, 4, 6, 8]
    possible_movement = [1]
    random_game = [True]

    summary = []
    for mode in random_game:
        #for inc_rounds in increase_of_rounds:
        for moves in possible_movement:
            for increase_of_map in size_of_map:
                avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, moves=moves, option=increase_of_map, use_random=mode)
                num_objects = len(settings.building_list) + len(settings.character_list) + len(settings.lamps_to_turn_off) + 17 + len(settings.hex_map) + len(settings.get_out_hex)

                summary.append({
                    "num_objects": num_objects,
                    "random": mode,
                    #"increase_rounds": inc_rounds,\
                    "moves": moves,
                    "avg_time": avg_time,
                    "avg_operations": avg_operations,
                    "avg_memory": avg_memory,
                    "avg_max_memory": avg_max_memory,
                    "detective_caught": type_of_finish["Detective caught Jack. Detective wins!"],
                    "jack_escape": type_of_finish["Jack managed to run away. Jack wins!"],
                    "jack_timeout": type_of_finish["Detective didn't manage to catch Jack in time. Jack wins!"]
                })
                print(f"Num_objects={num_objects}, Random={mode}, Moves={moves}, Avg time={avg_time:.6f}, Avg operations={avg_operations}, Avg memory={avg_memory}, Avg  max memory={avg_max_memory}")

                settings.reset()

    summary_df = pd.DataFrame(summary)
    summary_df.to_excel(filename, index=False)
    print(f"Wyniki zapisane do {filename}")
    return summary_df


def plot_summary(filename):
    summary_df = pd.read_excel(filename)
    # Jeśli w pliku pojawi się kolumna increase_rounds, rysujemy osobne linie
    # if "increase_rounds"  in summary_df.columns or "moves":
    #     increase_of_rounds = sorted(summary_df["increase_rounds"].unique())
    if "moves"  in summary_df.columns:
        moves = sorted(summary_df["moves"].unique())
        models = {"Log2": log_func}
    else:
        moves = [3]
        models = {"Linear": linear_func, "Log2": log_func}

    for mode in [False, True]:
        for type_of_y in ["avg_time", "avg_operations", "avg_memory", "avg_max_memory"]:
            if "memory" in type_of_y:
                models = {"Linear": linear_func}
            else:
                models = {"Log2": log_func}
            plt.figure(figsize=(8,6))

            print(f"\nRandom={mode}, Y={type_of_y}:")
            colors = ["red", "blue", "green", "orange", "pink", "purple", "brown", "gray"]
            #for idx, inc in enumerate(increase_of_rounds):
            for idx, inc in enumerate(moves):
                # filtrujemy po trybie i increase_rounds
                #subset = summary_df[(summary_df["random"] == mode) &(summary_df.get("increase_rounds", 0) == inc)].sort_values("num_objects")
                subset = summary_df[(summary_df["random"] == mode) &(summary_df.get("moves", 0) == inc)].sort_values("num_objects")
                x = subset["num_objects"].values
                y = subset[type_of_y].values
                color = colors[idx]
                #if "increase_rounds" not in summary_df.columns:
                plt.scatter(x, y, color=color)

                # dopasowanie funkcji
                for name, func in models.items():
                    try:
                        params, _ = curve_fit(func, x, y)
                        y_fit = func(x, *params)
                        mse = np.mean(np.abs(y - y_fit) / y)
                        if np.allclose(y, y[0], rtol=1e-5, atol=1e-8):
                            params[0] = 0 
                            y_fit = func(x, *params)
                        # plt.plot(x, y_fit, color = color, label=f"{name} fit, increase_rounds={inc} (MSE={mse:.6f})")
                        # print(f"{name} fit, increase_rounds={inc}: params={params}, MSE={mse:.6f}")
                        plt.plot(x, y_fit, color = color, label=f"{name} fit, moves={inc} (MSE={mse:.6f})")
                        print(f"{name} fit, moves={inc}: params={params}, MSE={mse:.6f}")
                    except Exception as e:
                        print(f"{name} fit failed, increase_rounds={inc}: {e}")

            plt.xlabel("Number of objects")
            label = {"avg_time": "Average simulation time [s]" , "avg_operations": "Average operations number", "avg_memory" : "Average memory [b]"}
            plt.ylabel(label[type_of_y] if type_of_y in label else "y")
            plt.title(f"{type_of_y} for Random={mode}")
            plt.legend()
            plt.grid(True)
            
            # ograniczenie osi Y do wartości dodatnich
            y_all = summary_df[(summary_df["random"] == mode)][type_of_y].values
            y_positive = y_all[y_all > 0]

            # dla liniowej
            #plt.ylim(bottom=min(y_positive)*(-0.9), top=max(y_positive)*1.1)
            plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=10))
            plt.ticklabel_format(style='plain', axis='y')


            plt.show()



if __name__ == "__main__":
    simulate_and_save(filename="simulation_movement_change_all_memory.xlsx")
    plot_summary("simulation_movement_change_all_memory.xlsx")
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
import os
        
def full_reset():
    for attr in ["hex_map", "building_list", "character_list", "lamps_to_turn_off", "get_out_hex"]:
        if hasattr(settings, attr):
            setattr(settings, attr, None)
    gc.collect()
    settings.reset()

#function to simulate one gameplay
def run_simulation(type_of_measurement, use_random=False, measure_memory = False ):
    if measure_memory:
        memory_amount = []
        tracemalloc.start()
    
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

#function to run simulations
def run_multiple_simulations(n=50, characters_amount = 8, scale_diff = 1, build_to_skip = None, increase_of_rounds = 0, moves = 3, characters = 8, option=0, use_random=False, double=False):
    full_reset()
    settings.col_row_hex = settings.init_col_row_hex()
    settings.random_game = use_random
    if option != None:
        map_switch.increase_the_map(settings.col_row_hex, option)
        if double:
            settings.max_rounds = characters_amount
        else:
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
    
    for type_of_measurement in ["operations", "memory"]:
        for _ in range(n):
            settings.reset()
            map_switch.change_char_list(characters_amount, settings.character_list)
            map_switch.prepare_the_map(option, settings.building_list, settings.character_list, settings.get_out_hex)
            map_switch.prepare_buildings(option*scale_diff, settings.building_list, settings.character_list, settings.get_out_hex, settings.hex_map, build_to_skip=build_to_skip)
            if type_of_measurement == "time":
                start_time = time.time()
                finish = run_simulation(type_of_measurement, use_random)    
                elapsed_time = time.time() - start_time
                results_time.append((elapsed_time*1000))
            elif type_of_measurement == "operations":
                finish = run_simulation(type_of_measurement, use_random) 
                results_operations.append(int(settings.operations)/(10^6))
            else:
                finish, result, peak = run_simulation(type_of_measurement, use_random, measure_memory=True) 
                results_memory.append(result/1024)
                results_max_memory.append(peak/1024)

            if finish in type_of_finish:
                type_of_finish[finish] += 1
    avg_time = np.mean(results_time)
    avg_operations = np.mean(results_operations)
    avg_memory = np.mean(results_memory)
    avg_highest_memory = np.mean(results_max_memory)
    return avg_time, avg_operations, avg_memory, avg_highest_memory, type_of_finish


# functions to fit
def linear_func(x, m, c):
    return m*x + c

def log_func(x, a, c):
    return a*np.log(x) + c

def log_lin(x, a, b, c):
    return a*np.log(x) + b*x + c

def power(x,a,b,c):
    return a * np.power(x, b) + c

def linear_log(x,a,b):
    return a*x*np.log(x) + b

def quadratic(x, a, b, c):
    return a*x**2 + b*x + c

def quadratic_lin(x, a, b, c):
    return a*x**2 + b*x

def quadratic_con(x, a,  c):
    return a*x**2 + c

def cubic_const(x,a,b):
    return a*x**3 + b

def cubic_lin_const(x,a,b,c ):
    return a*x**3 + b*x + c

def cubic(x,a,b,c, d):
    return a*x**3 + b*x**2 + c*x +d

def cubic_quad(x,a,b, d):
    return a*x**3 + b*x**2 + d

def quartic(x,a,b,c,d,e):
    return a*x**4 + b*x**3 + c*x**2 + d*x +e

def logistic_func(x, a, b1, c1, d1, b2, c2, d2):
    return a + b1 / (1 + np.exp(-c1*(x - d1))) + b2 / (1 + np.exp(-c2*(x - d2)))

def piecewise_3_jump(x, x1, x2, k1, k2, k3, b1, b2, b3):
    return np.piecewise(
        x,
        [x < x1, (x >= x1) & (x < x2), x >= x2],
        [lambda x: k1*x + b1,
         lambda x: k2*x + b2,
         lambda x: k3*x + b3]
    )

# function formulas to print
def function_formula(name, params):
    formula_templates = {
        "linear_func": "f(x) = {0}*x + {1}",
        "log_func": "f(x) = {0}*log2(x) + {1}",
        "linear_log": "f(x) = {0}x*log2(x) + {1}",
        "log_lin": "f(x) = {0}*log2(x) + {1}*x + {2}",
        "quadratic": "f(x) = {0}*x^2 + {1}*x + {2}",
        "quadratic_lin": "f(x) = {0}*x^2 + {1}*x",
        "quadratic_con": "f(x) = {0}*x^2 + {1}",
        "cubic_const": "f(x) = {0}*x^3 + {1}",
        "cubic_lin": "f(x) = {0}*x^3 + {1}*x + {2}",
        "cubic": "f(x) = {0}*x^3 + {1}*x^2 + {2}*x + {3}",
        "cubic_quad": "f(x) = {0}*x^3 + {1}*x^2 + {2}",
        "quartic": "f(x) = {0}*x**4 + {1}*x**3 + {2}*x**2 + {3}*x + {4}",
        "piecewise": "{2}*x + {5} for x<{0}, {3}*x + {6} for x>={0} and x<{1}, {4}*x + {7} for x>={1}",
        "power": "{0}*x^{1} + {2}"

    }

    template = formula_templates.get(
        name,
        "f(x) = " + " + ".join([f"{{{i}}}" for i in range(len(params))])
    )
    try:
        return template.format(*params)
    except Exception:
        return f"f(x) = {params}"

# function to simulate and save data to the excel file
def simulate_and_save(filename="simulation_summary.xlsx", element_type = "rounds"):
    size_of_map = list(range(0, 20, 1))
    match element_type:
        case "rounds":
            items = [0,1,2,3,4]
        case "moves":
            items = [1,3,5,7]
        case "characters":
            items = [4,8,12,16]
        case "characters and rounds":
            items = [4,8,12,16]
        case "buildings scale":
            items = [0, 0.5, 1]
        case "buildings": 
            items = ["sewer","apartament","lamp"]
        case _:
            print("Wrong type of element")
            return None
        
    random_game = [False, True]

    summary = []
    for mode in random_game:
        for item in items:
            for increase_of_map in size_of_map:
                match element_type:
                    case "rounds":
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, increase_of_rounds=item, option=increase_of_map, use_random=mode)
                    case "moves":
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, moves=item, option=increase_of_map, use_random=mode)
                    case "characters":
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, characters_amount=item, option=increase_of_map, use_random=mode)
                    case "characters and rounds":
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, characters_amount=item, option=increase_of_map, use_random=mode, double=True)
                    case "buildings scale":
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, scale_diff=item, option=increase_of_map, use_random=mode, double=True)
                    case "buildings": 
                        avg_time, avg_operations, avg_memory, avg_max_memory, type_of_finish = run_multiple_simulations(100, build_to_skip=item, option=increase_of_map, use_random=mode, double=True)
                    case _:
                        print("Wrong type of element")
                        return None
                
                num_objects = len(settings.building_list) + len(settings.character_list) + len(settings.lamps_to_turn_off) + 17 + len(settings.hex_map) + len(settings.get_out_hex)

                row = {
                    "num_objects": num_objects,
                    "random": mode,
                    f"{element_type}": item,
                    "avg_time": avg_time,
                    "avg_operations": avg_operations,
                    "avg_aux_memory": avg_memory,
                    "aux_memory": avg_max_memory,
                    "detective_caught": type_of_finish["Detective caught Jack. Detective wins!"],
                    "jack_escape": type_of_finish["Jack managed to run away. Jack wins!"],
                    "jack_timeout": type_of_finish["Detective didn't manage to catch Jack in time. Jack wins!"]
                }

                if not os.path.exists(filename):
                    pd.DataFrame([row]).to_excel(filename, index=False)  
                else:
                    with pd.ExcelWriter(filename, mode='a', if_sheet_exists='overlay') as writer:
                        startrow = writer.sheets['Sheet1'].max_row  
                        pd.DataFrame([row]).to_excel(writer, index=False, header=False, startrow=startrow)

                print(f"Num_objects={num_objects}, Random={mode}, {element_type}={item}, Avg time={avg_time:.6f}, Avg operations={avg_operations}, Avg aux memory={avg_memory}, Max aux memory={avg_max_memory}")


#function to plot a data
def plot_summary(filename):
    summary_df = pd.read_excel(filename)
    col = summary_df.iloc[:, 2]
    item = sorted(col.unique())

    for mode in [False,True]:
        for type_of_y in ["avg_time", "avg_operations", "aux_memory"]:
            # for comparing different elements
            if mode == False:
                if type_of_y == "avg_time" or type_of_y == "avg_operations":
                    models = {"cubic":cubic}
                else:
                    models = {"piecewise": piecewise_3_jump}
            else:
                if type_of_y == "avg_time" or type_of_y == "avg_operations":
                    models = {"power": power}
                else:
                    models = {"piecewise": piecewise_3_jump}

            # for comparing the models of functions
            # if mode == False:
            #     if type_of_y == "avg_time" or type_of_y == "avg_operations":
            #         models = {"quadratic":quadratic, "cubic":cubic, "quartic":quartic, "quadratic_con":quadratic_con, "cubic_const":cubic_const}
            #     else:
            #         models = {"piecewise": piecewise_3_jump, "linear": linear_func}
            # else:
            #     if type_of_y == "avg_time" or type_of_y == "avg_operations":
            #         models = {"power":power, "log_lin":log_lin, "log_func":log_func, "linear_func":linear_func}
            #     else:
            #         models = {"piecewise": piecewise_3_jump, "linear": linear_func}

            plt.figure(figsize=(8,6))

            print(f"\nRandom={mode}, Y={type_of_y}:")
            colors = ["red", "blue", "green", "orange", "purple", "pink", "brown", "gray"]
            
            for idx, inc in enumerate(item):
                subset = summary_df[(summary_df["random"] == mode) &(summary_df.get(summary_df.columns[2],0) == inc)].sort_values("num_objects")
                x = subset["num_objects"].values
                y = subset[type_of_y].values
                color = colors[idx]
                plt.scatter(x, y, color=color) # color = "black" when comparing models
                # index = 0
                for name, func in models.items():
                    # add only for comparing the models of function
                    # color = colors[index] 
                    # index += 1
                    # different models for precise functions for better fit
                    if mode == False and (summary_df.columns[2] == "buildings" or summary_df.columns[2] == "buildings scale"):
                        if (inc == 0 or inc=="sewer") and (type_of_y == "avg_time" or type_of_y=="avg_operations"):
                            name = "linear_func"
                            func = linear_func
                        elif inc == 0.5 and type_of_y=="avg_operations":
                            name = "cubic_const"
                            func = cubic_const
                    try:
                        if name == "logistic_func":
                            params, _ = curve_fit(func, x, y, p0 = [10600, 25000, 0.01, 1110, 100000, 0.005, 1620])

                        elif name == "piecewise":
                            match summary_df.columns[2]:
                                # starting parameters [x1, x2, k1, k2, k3, b1, b2, b3]
                                case "buildings scale": 
                                    if inc == 1:
                                        p0 = [450, 1600, 50, 300, 500, 0, 100000, 300000]
                                    elif inc == 0.5:
                                        p0 = [430, 1500, 50, 300, 500, 0, 100000, 300000]
                                    else:
                                        p0 = [370, 1350, 50, 300, 500, 0, 100000, 300000]
                                case "buildings":
                                    if inc == "apartament":
                                        p0 = [416, 1480, 50, 300, 500, 0, 100000, 300000]
                                    elif inc == "lamp":
                                        p0 = [430, 1560, 50, 300, 500, 0, 100000, 300000]
                                    elif inc == "sewer":
                                        p0 = [440, 1550, 50, 300, 500, 0, 100000, 300000]
                                    else:
                                        p0 = [450, 1600, 50, 300, 500, 0, 100000, 300000]
                                case _:
                                    p0 = [450, 1600, 50, 300, 500, 0, 100000, 300000]
                            params, _ = curve_fit(func, x, y, p0=p0, maxfev=20000)
                        else:
                            params, _ = curve_fit(func, x, y)

                        y_fit = func(x, *params)
                        mse = np.mean(np.abs(y - y_fit) / y)
                        if np.allclose(y, y[0], rtol=1e-5, atol=1e-8):
                            params[0] = 0 
                            y_fit = func(x, *params)
                        formula = function_formula(name, params)
                        plt.plot(x, y_fit, color = color, label=f"{name} fit, {summary_df.columns[2]}={inc} (MSE={mse:.6f})")
                        print(f"{name} fit, change={inc}: {formula}, MSE={mse:.6f}")
                    except Exception as e:
                        print(f"{name} fit failed, {summary_df.columns[2]}={inc}: {e}")

            plt.xlabel("Number of objects")
            label = {"avg_time": "Average simulation time [ms]" , "avg_operations": "Average operations number", "aux_memory" : "Average auxiliary memory [kb]", "all_memory" : "Average all memory [kb]"}
            plt.ylabel(label[type_of_y] if type_of_y in label else "y")
            if type_of_y == "avg_operations":
                plt.annotate(r'$\times 10^6$', xy=(0, 1.02), xycoords='axes fraction', ha='left', va='bottom')
            title = {"avg_time": "Execution time" , "avg_operations": "Number of operations", "aux_memory" : "Memory usage", "all_memory" : "Memory usage"}
            mode_name = "random strategy" if mode else "heurystic strategy"
            if filename == "comparison.xlsx":
                plt.title(f"{title[type_of_y]} - comparison of function models \nfor {mode_name}")
            else:
                plt.title(f"{title[type_of_y]} depending on number of \n{summary_df.columns[2]} - {mode_name}")
            plt.legend()
            plt.grid(True)
            
            plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=10))
            plt.ticklabel_format(style='plain', axis='y')


            plt.show()



if __name__ == "__main__":
    simulate_and_save("simulation_rounds_change.xlsx", "rounds")
    simulate_and_save("simulation_movements_change.xlsx", "moves")
    simulate_and_save("simulation_characters_change.xlsx", "characters")
    simulate_and_save("simulation_rounds_characters_change.xlsx","characters and rounds")
    simulate_and_save("simulation_buildings_scale_change.xlsx","buildings scale")
    simulate_and_save("simulation_buildings_change.xlsx","buildings")
    #plot_summary("simulation_rounds_change.xlsx")
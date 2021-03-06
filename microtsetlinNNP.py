#PYTHON VERSION > 3
import numpy as np
import itertools

LIT,NOT_LIT   = 0,1 #LIT = postive literal
REWARD,INACTION,PENALTY = 0,1,2 
NO_ACT, ACT             = 0,1

s = 3.9
B = (s-1.0)/s
L = 1.0/s

u = [
#(r,i,p) (y_est,pol   ,c,l,i/e)   
 (L,B,0) #(0,0 (-1),0,0,0)	
,(0,B,L) #(0,0 (-1),0,0,1)	
,(L,B,0) #(0,0 (-1),0,1,0)	
,(0,B,L) #(0,0 (-1),0,1,1)	
,(L,B,0) #(0,0 (-1),1,0,0)	
,(0,B,L) #(0,0 (-1),1,0,1)	
,(0,L,B) #(0,0 (-1),1,1,0)	
,(B,L,0) #(0,0 (-1),1,1,1)	
,0       #(0,1     ,0,0,0)	
,0       #(0,1     ,0,0,1)	
,0       #(0,1     ,0,1,0)	
,0       #(0,1     ,0,1,1)	
,(0,0,1) #(0,1     ,1,0,0)	
,0       #(0,1     ,1,0,1)	
,0       #(0,1     ,1,1,0)	
,0       #(0,1     ,1,1,1)	
,0       #(1,0 (-1),0,0,0)		 
,0       #(1,0 (-1),0,0,1)		 
,0       #(1,0 (-1),0,1,0)		 
,0       #(1,0 (-1),0,1,1)		 
,(0,0,1) #(1,0 (-1),1,0,0)		 
,0       #(1,0 (-1),1,0,1)	
,0       #(1,0 (-1),1,1,0)	
,0       #(1,0 (-1),1,1,1)	
,(L,B,0) #(1,1     ,0,0,0)		
,(0,B,L) #(1,1     ,0,0,1)		
,(L,B,0) #(1,1     ,0,1,0)		
,(0,B,L) #(1,1     ,0,1,1)		
,(L,B,0) #(1,1     ,1,0,0)		
,(0,B,L) #(1,1     ,1,0,1)	
,(0,L,B) #(1,1     ,1,1,0)	
,(B,L,0) #(1,1     ,1,1,1)	
]
# write my own choice function
#implement deterministic randomness 

r_base = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
rand_proxy = itertools.cycle(r_base)
rand_proxy2 = itertools.cycle(r_base)
# rewrite the choice function
import random

def my_choice(out_list,prob_list):
    #generate a random number
    my_rand = next(rand_proxy)

    #my_rand = random.random()
    assert(sum(prob_list) == 1.0)
    accum = 0.0
    for i,j in enumerate(prob_list):
        accum += j
        if my_rand <= accum:
            return out_list[i]

def calc_all_clause_outputs(x_hat, tsetlin, prune = False):  
    """Calculate all clauses using the fact that any FALSE in an AND statement terminates
    an AND. 
    """
    num_c, num_f = num_clauses,num_features             
    def calc_clause_output(c):
        """output is a tuple (x,bool), where bool is whether the clause has used literals"""
        used = 0  
        for f in range(num_f):
            used += action(tsetlin[c][f][LIT]) + action(tsetlin[c][f][NOT_LIT])
            if (action(tsetlin[c][f][LIT]) == ACT and x_hat[f] == 0) or (action(tsetlin[c][f][NOT_LIT]) == ACT and x_hat[f] == 1):
                return (0,True)
        live = True if not prune else (used != 0)
        return (1, live)     
    return [calc_clause_output(c) for c in range(num_c)]

def update(t_in,y_hat,polarity,clause_output,x_hat,tsetlin,T = 15):
    """ Perform tsetlin array update."""
    num_c, num_f = num_clauses,num_features

    t_d = max(-T, min(T,t_in))
    p_update = 1.0*(T - t_d)/(2*T) if y_hat == 1  else 1.0*(T + t_d)/(2*T)
    y_sft= y_hat << 4
    for c in range(num_c):
        c_out, live  = clause_output[c]
        if  ( next(rand_proxy2) <= p_update) and live:
            p_sft = polarity[c] << 3
            c_sft = c_out << 2
            for f in range(num_f):
                for s in [LIT,NOT_LIT]:
                    x_d = x_hat[f] if s == LIT else (1 - x_hat[f])
                    x_sft = x_d << 1 
                    update_tuple = u[y_sft|p_sft|c_sft|x_sft|action(tsetlin[c][f][s])]
                    if update_tuple != 0:
                        update_action = my_choice([REWARD,INACTION,PENALTY],update_tuple)
                        if update_action == REWARD:
                            if action(tsetlin[c][f][s]) == NO_ACT:
                                tsetlin[c][f][s] -= 1
                                if tsetlin[c][f][s] < MINSTATE : tsetlin[c][f][s] = MINSTATE
                            else:
                                tsetlin[c][f][s] += 1 
                                if tsetlin[c][f][s] > MAXSTATE : tsetlin[c][f][s] = MAXSTATE
                        elif update_action == INACTION:
                            pass
                        elif update_action == PENALTY:
                            if action(tsetlin[c][f][s]) == ACT:
                                tsetlin[c][f][s] -= 1
                            else:
                                tsetlin[c][f][s] += 1

X = [[0,0],[0,1],[1,0],[1,1]]
Y = [0,1,1,0]

def build_ndim_array(X,Y,Z,n1,n2):
    out = []
    for x in range(X):
        out += [[]]
        for y in range(Y):
            out[-1] += [[]]
            for z in range(Z):
                out[-1][-1] += [my_choice([n1,n2],[0.5,0.5])]
    return out

num_features  = len(X[0])
num_clauses   = 10  #must be even 
num_c2        = num_clauses//2
MAXSTATE      = 100 #must be even
MINSTATE      = 1
MIDSTATE      = MAXSTATE//2  
action        = lambda state: NO_ACT if state <= MIDSTATE else ACT #note: MIDSTATE = INACTION 
tsetlin = build_ndim_array(num_clauses,num_features, len([LIT,NOT_LIT]),MIDSTATE, MIDSTATE+1)
# I deviate from the paper slightly by grouping signs together - this is to make reading the propositions easier
clause_sign   = np.array(num_c2*[1] + num_c2*[-1]) 
polarity      = np.array(num_c2*[1] + num_c2*[0] ) 
iterations    = 20

def train():
    for i in range(iterations):
        e = 0
        out = []
        for x_hat,y_hat in zip(X,Y):
            clause_output = calc_all_clause_outputs(x_hat, tsetlin)
            tot_c_outputs = np.sum([c_out*sign if live else 0 for (c_out,live),sign in zip(clause_output,clause_sign)])
            out += [tot_c_outputs]
            y_est = 1 if tot_c_outputs >= 0 else 0 #nte: total 0 = output 1
            e += 1 if y_est != y_hat else 0
            if np.random.random() < 0.1:
                y_hat = 1 - y_hat
            update(tot_c_outputs,y_hat,polarity,clause_output,x_hat,tsetlin,T=4)
        print("it", i, e,out)

import timeit
f = timeit.timeit(train,number=10)
print(f)
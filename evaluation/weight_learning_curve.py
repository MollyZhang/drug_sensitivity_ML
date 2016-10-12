"""parse weight updates from PSL debug log and plot the rule weight change over iterations
"""

def main():
    weights = parse_weight("../psl/result/first_model_cross_val_fold1_log.txt")
    print weights


def parse_weight(log_file):
    rule_text = {"} ( DRUGTARGET(D, G) & ESSENTIAL(C, G) ) >> SENSITIVE(C, D)": "essential_rule",
                 "} ( DRUGTARGET(D, G) & ACTIVE(C, G) ) >> SENSITIVE(C, D)": "active_rule",
                 "} ~( SENSITIVE(C, D) )": "sensitive_prior"}
    weights = {"active_rule": [], "essential_rule": [], "sensitive_prior": []}
    
    f = open(log_file, "r")
    all_lines = f.readlines()
    f.close()
    
    for rule_text, rule in rule_text.iteritems():
        weights[rule] = [float(line.split(rule_text)[0].split("{")[-1])
                         for line in all_lines
                         if (rule_text in line and "kernel" in line)]
    return weights





if __name__ == "__main__":
    main()

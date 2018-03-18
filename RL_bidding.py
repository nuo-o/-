class RLB_DP_I:
    up_precision = 1e-10
    zero_precision = 1e-12

    def __init__(self, auction, train_thetaAvg):
        self.theta_avg = train_thetaAvg
        self.V = []
        self.D = []
        
    def calc_optimal_value_function_with_approximation_i(self, N, B, max_bid, m_pdf, save_path):
        V_out = open(save_path, "w")
        V = [0] * (B + 1)
        nV = [0] * (B + 1)
        V_max = 0
        a_max = max_bid
        
        for b in range(0, a_max + 1):
            V_max += m_pdf[b] * self.theta_avg
            
        for n in range(1, N):
            a = [0] * (B + 1)
            bb = B - 1
            
            for b in range(B, 0, -1):
                while bb >= 0 and (V[bb] - V[b] + self.theta_avg) >= 0:
                    bb -= 1
                if bb < 0:
                    a[b] = min(max_bid, b)
                else:
                    a[b] = min(max_bid, b - bb - 1)

            for b in range(0, B):
                V_out.write("{}\t".format(V[b]))
                
            V_out.write("{}\n".format(V[B]))

            flag = False
            for b in range(1, B + 1):
                
                nV[b] = V[b]
                
                for delta in range(0, a[b] + 1):
                    
                    nV[b] += m_pdf[delta] * (self.theta_avg + V[b - delta] - V[b]) # V[b] 是递增函数，因此，nV[b] 最大值就是
                
                if abs(nV[b] - V_max) < self.up_precision: # early stop, as V[b-delta] = V[b]                   
                    for bb in range(b + 1, B + 1):
                        nV[bb] = V_max
                    flag = True
                    break
            V = nV[:]
            
        for b in range(0, B):
            V_out.write("{0}\t".format(V[b]))
        V_out.write("{0}\n".format(V[B]))
        V_out.flush()
        V_out.close()


    def load_value_function(self, N, B, model_path):
        self.V = [[0 for i in range(B + 1)] for j in range(N)]
        with open(model_path, "r") as fin:
            n = 0
            for line in fin:
                line = line[:len(line) - 1].split("\t")
                for b in range(B + 1):
                    self.V[n][b] = float(line[b])
                n += 1
                if n >= N:
                    break

    def bid(self, n, b, theta, max_bid):
        a = 0
        if len(self.V) > 0:
            for delta in range(1, min(b, max_bid) + 1):
                if theta + (self.V[n - 1][b - delta] - self.V[n - 1][b]) >= 0:
                    a = delta
                else:
                    break
        return a

    def run(self, B, auction_df, pCTR, bid_log_path, N, max_bid, save_log=False, evaluate = False):
        auction = 0
        imp = 0
        clk = 0
        cost = 0
        bid_price = []

        if save_log:
            log_in = open(bid_log_path, "w")

        episode = 1
        n = N
        b = B
        for i in range(len(auction_df)):
            
            theta = pCTR[i]
            a = self.bid(n, b, theta, max_bid)
            a = min(int(a), min(b, max_bid))
            bid_price.append(a)
            
            if evaluate:
                click = auction_df.iloc[i]['click']
                price = auction_df.iloc[i]['payprice']
                
                if a >= price:
                    imp += 1
                    clk += click
                    b -= price
                    cost += price
            
                log = "\t{}\t{}_{}\t{}_{}_{}\t{}_{}\t".format(episode, b, n, a, price, click, clk, imp)
            
                if save_log:
                    log_in.write(log + "\n")

            n -= 1
            auction += 1

            if n == 0:
                episode += 1
                n = N
                b = B
                
        if save_log:
            log_in.flush()
            log_in.close()

        return bid_price, auction, imp, clk, cost



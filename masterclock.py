import itertools
import time
import asyncio

class MasterClock:
    def __init__(self, clockdur):
        self.clock = 0
        self.clockdur = clockdur
        self.tickers = []
        self.pending_delete_tickers = []
        self.waiters = []
        self.tick_cb = None
        
    def add_ticker(self, tok):
        self.tickers.append(tok)

    def remove_ticker(self, tok):
        # delay removal until safe time
        self.pending_delete_tickers.append(tok)
        
    def delay(self, ticks):
        fut = asyncio.get_running_loop().create_future()
        self.waiters.append((self.clock + ticks, fut))
        return fut

    def count(self):
        return self.clock
    
    # called after all the clockers were run.
    def set_tick_cb(self, cb):
        self.tick_cb = cb
        
    async def run(self):
        all_finished = False
        while len(self.tickers) > 0:
            #print(f"waiters {self.clock}")
            # wake up waiters:
            do_yield = False
            for i in range(len(self.waiters) - 1, -1, -1):
                waiter = self.waiters[i]
                if waiter[0] <= self.clock:
                    #print("wake up")
                    do_yield = True
                    waiter[1].set_result(self.clock)
                    del self.waiters[i]
                if do_yield:
                    await asyncio.sleep(0)
                        
            #print(f"master tick {self.clock}")
            updated = False
            for tick in self.tickers:
                if tick.tok(self.clock):
                    updated = True
            if self.tick_cb != None:
                self.tick_cb(updated)
            if len(self.pending_delete_tickers) > 0:
                for tok in self.pending_delete_tickers:
                    self.tickers.remove(tok)
            
            self.clock += 1
            await asyncio.sleep(self.clockdur)
        print("master clock finished")
        

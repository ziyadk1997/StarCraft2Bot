#Import All Things Needed
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS,PROBE,PYLON,ASSIMILATOR,GATEWAY,CYBERNETICSCORE,STALKER,STARGATE,VOIDRAY
import random

#Bot Class
class LOZ(sc2.BotAI):
    #Initialize Attributes
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
    # On each Iteration what to do
    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
    #Build Workers
    async def build_workers(self):
        #check that no more than 16 workers for each NEXUS and max limit for workers has not been reached
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
                #check if can afford to build worker
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    #Building Pylons
    async def build_pylons(self):
        #check if supply is low and no other pylons are being built
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                #check if can afford to build pylon
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)


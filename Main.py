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
#Build Assimilators
    async def build_assimilators(self):
        #loop on all ready nexuses
        for nexus in self.units(NEXUS).ready:
            #get vespenes that are close to the nexus
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            #loop on vaspenes
            for vaspene in vaspenes:
                worker = self.select_build_worker(vaspene.position)
                # break if not enough resources or no worker found
                if not self.can_afford(ASSIMILATOR) or worker is None:
                    break
                #if there is no close by assimilator let worker build assimilator
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))
    #Expand Nexus 
    #Already predefined in sc2.BotAI but call it under condition
    async def expand(self):
        #Expand by rate 1 per minute if can afford it
        if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
            await self.expand_now()
     #build buildings that build enemies
    async def offensive_force_buildings(self):
        #if there is a ready pylon
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            #build cyberneticscore if not already building and can afford
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)
            #build gateway if not already building and can afford
            elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)
            #build stargate if not already building and can afford
            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)
    #Build Enemies
    async def build_offensive_force(self):
        #let every gateway create a stalker if it is ready and can afford
        for gw in self.units(GATEWAY).ready.noqueue:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))
        # let every stargate create a voidray if it is ready and can afford
        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))

import logging
import re
import time
import os
import json
import gevent

from Config import config
from Plugin import PluginManager

allow_reload = False  # No reload supported

log = logging.getLogger("ZeronameExPlugin")

loggerx = log

@PluginManager.registerTo("SiteManager")
class SiteManagerPlugin(object):
    def initZeroNameCachedPlugin(self, *args, **kwargs):
        self.debugme = True
        self.logme = loggerx
        if not self.debugme:
           def _debug(message):
               return
           self.logme.debug = _debug
           
        self.zero_names = []
        self.count = 0
        self.dcr = re.compile(r"(.*?)([A-Za-z0-9_-]+\.bit)$")
        self.acr = re.compile("^[A-Za-z0-9]{26,35}$")
        self.my_db_domains = {}
        self.zero_db_domains = {}
        self.zero_content_json_domains = {}
        self.load_cache()

    def loadZeroNameCachedPlugin(self, *args, **kwargs):
        self.load_cache()
        self.count = self.count + 1
        self.logme.debug("ZeroNameExPlugin bit_resolver count: " + str(self.count))
        if not self.zero_names:
           self.zero_names = []
           def get_zero_name_obj():
               zero_name_obj = {
                    "site_zeroname": None,
                    "site_zeroname_modified": 0,
                    "db_domains": {},
                    "db_domains_modified": 0,
                    "bit_resolver": None,
                    "loaded": False
               }
               class ZeroNameObj(object):
                     def __init__(self, *args, **kwargs):
                         self.__dict__.update(zero_name_obj)
               return ZeroNameObj
               
           self.create_zno = get_zero_name_obj()

        for bit_resolver in self.zero_cache["resolvers"]:
            zno = self.create_zno()
            self.logme.debug("ZeroNameCachedPlugin bit_resolver: " + bit_resolver)
            zno.bit_resolver = bit_resolver
            zno.site_zeroname = self.need(bit_resolver)
            self.zero_names.append(zno)
        self.update_cache()

    def __init__(self, *args, **kwargs):
        super(SiteManagerPlugin, self).__init__(*args, **kwargs)
        self.initZeroNameCachedPlugin()

        
    def load_cache(self):
        if hasattr(self, "zero_cache"):
           return

        self.cache_file_path = os.path.dirname(os.path.abspath(__file__)) + "/ZeroNameExPlugin.json"
        if not os.path.isfile(self.cache_file_path):
           zero_cache = {
              "domains": {},
              "content_json_addresses": {},
              "content_json_domains": {},
              "update_interval": 3600 * 5, # 5 hours is really enough and not too much, real dns resolvers need 24 hours by the way >.<
              "last_updated": 0,
              "update_time": 0,
              "use_cache": True,
              "resolvers": config.bit_resolvers,
              "main_resolver": config.bit_resolver
           }
           with open(self.cache_file_path, 'w') as f: 
                json.dump(zero_cache, f, indent=2, sort_keys=True)
        
        with open(self.cache_file_path, 'r') as f: 
             self.zero_cache = json.load(f)

    def update_cache_content_json(self):
        self.load_cache()
        if not self.cache_need_update():
           return
        
        content_json_domains = self.filter_domains(self.zero_cache["content_json_domains"])
        self.zero_cache["content_json_domains"] = content_json_domains
        self.zero_content_json_domains = self.zero_cache["content_json_domains"]
        self.zero_cache["last_updated"] = time.time()
        self.update_cache_file()
        
    def update_cache(self):
        self.load_cache()
        if not self.cache_need_update():
           return

        zero_names_len = len(self.zero_names)
        for i in range(0, zero_names_len):
            self.loadZeroName(i)
            self.update_cache_resolver(i)
        
        content_json_domains = self.filter_domains(self.zero_cache["content_json_domains"])
        
        self.zero_db_domains = self.zero_cache["domains"]
        self.zero_content_json_domains = self.zero_cache["content_json_domains"]
        self.zero_cache["content_json_domains"] = content_json_domains
        self.zero_cache["last_updated"] = time.time()
        self.update_cache_file()

    def update_cache_resolver(self, i):
        self.load_cache()
        self.zero_cache["domains"].update(self.zero_names[i].db_domains)
        domains = self.filter_domains(self.zero_cache["domains"])
        self.zero_cache["domains"] = domains
        self.zero_cache["last_updated"] = time.time()

    def update_cache_file(self):
        try:
            self.load_cache()
            with open(self.cache_file_path, 'w') as f:        
                 json.dump(self.zero_cache, f, indent=2, sort_keys=True)        
        except:
            pass

    def cache_need_update(self):
        self.load_cache()
        last_updated = self.zero_cache["last_updated"]
        update_interval = self.zero_cache["update_interval"]
        if update_interval <= 0:
           return True
           
        if last_updated <= 0:
           return True

        last_updated = last_updated + update_interval
        if time.time() >= last_updated:
           return True
           
        return False
           
    def get_item_from_zero_cache(self, item):
        self.update_cache()
        return self.zero_db_domains.get(item)
        
    def filter_domains(self, my_dict):
        result = filter(lambda x: self.dcr.match(x[0]) and self.acr.match(x[1]) and  (x[0], x[1]) or False, my_dict.items())
        result = dict(result)
        return my_dict

    # Return: Site object or None if not found
    def fast_get(self, address):
        return self.sites.get(address) or self.sites.get(address.lower())

    # Return or create site and start download site files
    def fast_need(self, address, all_file=True, settings=None):
        site = self.fast_get(address)
        from Site.Site import Site
        if not site:  # Site not exist yet
            self.sites_changed = int(time.time())
            if not self.acr.match(address):
               return False  # Not address: %s % address
            self.logme.debug("Added new site: %s" % address)
            config.loadTrackersFile()
            site = Site(address, settings=settings)
            self.sites[address] = site
            if not site.settings["serving"]:  # Maybe it was deleted before
                site.settings["serving"] = True
            site.saveSettings()
            if all_file:  # Also download user files on first sync
               site.download(check_size=True, blind_includes=True)

        return site
             
    #Return: see resolveBitDomain from the ZeroName Plugin
    def loadZeroName(self, i):
        zno = self.zero_names[i]
             
        #self.logme.debug("ZeroNameCachedPlugin zno: " + zno)
        self.logme.debug("ZeroNameCached: Resolve from : %s" % zno.bit_resolver)
        if not zno.site_zeroname:
           zno.site_zeroname = self.fast_need(zno.bit_resolver)
           self.logme.debug("ZeroNameCached: Load site site_zeroname : %s" % zno.bit_resolver)

        zno.site_zeroname_modified = zno.site_zeroname.content_manager.contents.get("content.json", {}).get("modified", 0)
        self.logme.debug("ZeroNameCached: test zno.db_domains_modified != zno.site_zeroname_modified ")
        if (not zno.loaded) or (zno.db_domains_modified != zno.site_zeroname_modified):
            zno.site_zeroname.needFile("data/names.json", priority=10)
            self.logme.debug("ZeroNameCached: needFile")
            s = time.time()
            try:
                zno.db_domains = self.filter_domains(zno.site_zeroname.storage.loadJson("data/names.json"))
                zno.loaded = True
                zno.db_domains_modified = zno.site_zeroname_modified
                self.logme.debug(
                    "ZeroNameCached: Domain db with %s entries loaded in %.3fs (modification: %s -> %s)" %
                   (len(zno.db_domains), time.time() - s, zno.db_domains_modified, zno.site_zeroname_modified)
                )                 
            except Exception as err:
                log.error("ZeroNameCached: Error loading names.json: %s" % err)
                zno.loaded = False

        self.zero_names[i] = zno
        
    def load(self, *args, **kwargs):
        super(SiteManagerPlugin, self).load(*args, **kwargs)
        self.loadZeroNameCachedPlugin()
               
    # Turn domain into address
    def resolveDomain(self, domain):
        log.debug("resolve domain " + domain)
        old_my_db_domains_modified = 0
        new_my_db_domains_modified = 0
        has_db_domains_modified = "db_domains_modified" in super(SiteManagerPlugin, self).__dict__
        if has_db_domains_modified:
           old_my_db_domains_modified = super(SiteManagerPlugin, self).__dict__["db_domains_modified"]
        resolve = super(SiteManagerPlugin, self).resolveDomain(domain)
        if has_db_domains_modified:
           new_my_db_domains_modified = super(SiteManagerPlugin, self).__dict__["db_domains_modified"]
        
        log.debug("old_my_db_domains_modified " + str(old_my_db_domains_modified))
        log.debug("new_my_db_domains_modified " + str(new_my_db_domains_modified))
        
        if self.cache_need_update():
           self.update_cache()
           self.my_db_domains = {}
           old_my_db_domains_modified = 0
           new_my_db_domains_modified = 0
           
        if new_my_db_domains_modified != old_my_db_domains_modified or len(self.my_db_domains) == 0:
           has_db_domains = "db_domains" in super(SiteManagerPlugin, self).__dict__
           if has_db_domains:
              my_db_domains = super(SiteManagerPlugin, self).__dict__["db_domains"]
              if my_db_domains == None:
                 log.debug("my_db_domains is None")
                 return resolve
              new_domains = {}
              new_domains.update(self.zero_content_json_domains)
              new_domains.update(self.zero_db_domains)
              new_domains.update(my_db_domains)
              self.my_db_domains = my_db_domains
              super(SiteManagerPlugin, self).__dict__["db_domains"] = self.my_db_domains
              log.debug("my_db_domains is funzed yayy  yay yaayy")
              return self.my_db_domains.get(domain)
           else:
              return resolve
        return resolve

    # Return: True if the address is domain
    def isDomain(self, address):
        log.debug("is domain " + address)
        isDomainZite = super(SiteManagerPlugin, self).isDomain(address)
        if not isDomainZite:
           if self.zero_cache["content_json_addresses"].get(address):
              return isDomainZite
           has_sites = "sites" in super(SiteManagerPlugin, self).__dict__
           if not has_sites:
              return isDomainZite
           
           sites = super(SiteManagerPlugin, self).__dict__["sites"]
           
           site = sites.get(address)
           if not site:
              return isDomainZite
           
           contentJson = site.content_manager.contents.get("content.json")
           if not contentJson:
              return isDomainZite
           
           domain = contentJson.get("domain")
           if not domain:
              return isDomainZite
           
           if not self.zero_cache["content_json_domains"].get(domain):
              nd = {}
              nd[domain] = address  
              na = {}             
              na[address] = domain   
              self.zero_cache["content_json_domains"].update(nd)
              self.zero_cache["content_json_addresses"].update(na)
              self.zero_content_json_domains = self.zero_cache["content_json_domains"]
              self.zero_cache["last_updated"] = 0
              
        return isDomainZite 
       

@PluginManager.registerTo("ConfigPlugin")
class ConfigPlugin(object):
    def createArguments(self):
        group = self.parser.add_argument_group("ZeronameExPlugin")
        group.add_argument(
            "--bit_resolvers", help="ZeroNameEx: ZeroNet sites to resolve .bit domains",
            default=["1Name2NXVi1RDPDgf5617UoW7xA6YrhM9F", "1SitesVCdgNfHojzf2aGKQrD4dteAZR1k", "1E97TpiDiCj1WGhZWxoKjBV9KkVty1PFsq"], nargs='+', metavar="0net_addresses"
        )            # zeronet resolver,                     # zeronetx resolver                # zeronet is nice resolver

        log.debug("ZeroNameEx has created the arguments for you!")
        return super(ConfigPlugin, self).createArguments()      
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
        self.zero_yo_domains = {}
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

    def get_yo_domains(self):
        return {
            'katian-blog.zn': 'http://127.0.0.1:43110/1DgZjVXNqyq9ScsNcz48Df5iVFpf3RgFfd/',
            'katian.zn': '12245YXgK5vAbcrhzT84yQVW3XSQDLfeuA',
            'lastone.zn': '1LJ3r1Zf1F3qFXw3E4QBvgaNzsFhAixQL2',
            '0clock.yo': '1zatLeyRNeBoYfFJP3j9Jywwcz68fheR6',
            'ns-game.yu': '12bD4na9Ux7fbfzcmfBRuLWbjMWTAiuaLk',
            'ns-game.yo': '12bD4na9Ux7fbfzcmfBRuLWbjMWTAiuaLk',
            'ns-game.zn': '12bD4na9Ux7fbfzcmfBRuLWbjMWTAiuaLk',
            '3dporno.yo': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            '3dporno.zn': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            'krylov.zn': '127.0.0.1',
            'ns-game.of': '12bD4na9Ux7fbfzcmfBRuLWbjMWTAiuaLk',
            'ruzerotalk.yu': '1Apr5ba6u9Nz6eFASmFrefGvyBKkM76QgE',
            'ruzerotalk.zn': '1Apr5ba6u9Nz6eFASmFrefGvyBKkM76QgE',
            '0clock.zn': '1zatLeyRNeBoYfFJP3j9Jywwcz68fheR6',
            'paper.yo': '1LJ3r1Zf1F3qFXw3E4QBvgaNzsFhAixQL2',
            'one.zn': '1LJ3r1Zf1F3qFXw3E4QBvgaNzsFhAixQL2',
            'ruzerotalk.yo': '1Apr5ba6u9Nz6eFASmFrefGvyBKkM76QgE',
            'gledos.zn': '12g7awE9MuhtHzv4o1PukjiaQdtvvbpxbP',
            '3dporno.list': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            'zero-wiki-fr.zn': '135qYXdNpf5kTWYuTJ8uautsUi91Bhvcck',
            '3dporno.inf': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            '3dporno.of': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            '3dporno.yu': '16cYTZiW45hZ1tQCVVth5ZVqNe2ZZAWUFk',
            '2048.zn': '14CJiCfKCbALS3HnwfFV6GJ6ixXKdzDz2g',
            'gay.3dporno.zn': '1Gay3DR1K69PoqMukjShz9sPiWqUSLtVxt',
            'g6534gf546g5.yo': 'http://127.0.0.1:43110/Talk.ZeroNetwork.bit',
            'qqqqqqqqqqqqq.yo': 'qqqqqqqqq',
            'qqqqqqqqqqqqqqqqq.yo': 'qqqqqqqqqqqq',
            'qqqqqqqqqqqqqqqqqqqqqqq.yo': 'qqqqqqqqqqqqqqqqqqq',
            'xxx.list': '127.0.0.1',
            'kxonetwork.yo': '1GTVetvjTEriCMzKzWSP9FahYoMPy6BG1P',
            'shirukatutorials.yo': '1KGXoRuM7Q4rYHcTZod442HQhq95UEFW5',
            'tui.yu': '1BzpRTB6DHjdCkfSRW8sU2V5GuFMnhWkGK',
            'filips.yo': 'TODO',
            'donda.yo': '17dqsM2zdrkAn2HGPxad6sExBut8U3cajc',
            'ua.list': '1UkrrSpnJmuiig6r5v88Kn3isaR64Fbh3',
            'zeroframe.zn': 'TODO',
            'peermessage.zn': 'TODO, mail gitcenter@mail.zeronetwork.bit if this TODO has been here for a year',
            'kaffie.zn': '1A83ijw3boqTtqdLz8me7AqeK1nEK8yxeu',
            'kaffiene.zn': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'blog.kaffie.zn': '1N6zp6jCXPBktNMPfe7UJBpQGyfCq7k2M8',
            'spam.list': '1CufK1ZtvekbFXEpSyKT2gDjf9jnqW8KwG',
            'news.zn': '1NEwsvyrAoEWU64ZozwdfgEUQhwxiCrh1t',
            'galleries.zn': '1PGaLLNiadMzrmw6MMMnpZnskwFcdgZoS4',
            'block.list': '127.0.0.1',
            'black.list': '127.0.0.1',
            'white.list': '127.0.0.1',
            'shit.list': '127.0.0.1',
            'galleryhub.zn': '14NFfVBBAFbNdqX4nyGjyBF1BRSz7jn2QP',
            'anshorei.zn': '13T79X7tG8Fi3EZCev3xU1wYTtFHHnqWGQ',
            'play.zn': '1Ag6xidDHiPgWoDKhfSx4xFQr6WC3NqxZg',
            'arkid.zn': 'ARKidcu9P7HTpig7htMsxTgEuUAp3h34qg',
            'kxoid.zn': '12F5SvxoPR128aiudte78h8pY7mobroG6V',
            'vacation.zn': '1HcLPSR5ss1ehsqP8kU2Sa2TJyDVcGADTp',
            'alotaplot.zn': '1G8VWDQc5fXLkRiijJB4EZerDLmDVY75MZ',
            'monitor.peermessage.zn': '1E7AmfXMkfbV2Gg83Harp4PHan7BdvSuEg',
            'hentaitalk.zn': '1KcWtJi2YSvL9DwouGymLZPKy9N6rTGXLt',
            'anthology.zn': 'TODO Anthology.jp/zn releasing later this year',
            'p.zn': '1PLAYgDQboKojowD3kwdb3CtWmWaokXvfp',
            'polbooks.zn': '1BGYb8Qyq5ApUG6ZNkASczzePf8c87Li82',
            'anshorei.yu': '13T79X7tG8Fi3EZCev3xU1wYTtFHHnqWGQ',
            'gohzer.yo': 'localhost',
            'sw0gger.yo': 'localhost',
            'name.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'kiwipedia.yo': '1KiwiBCVBUcuypVm8FEmUW9YT6fJDXkN9r',
            'gitcenter.yo': '1GitLiXB6t5r8vuU2zC6a8GYj9ME6HMQ4t',
            'index.gitcenter.yo': '1iNDExENNBsfHc6SKmy1HaeasHhm3RPcL',
            'repo.gitcenter.yo': '1RepoXU8bQE9m7ssNwL4nnxBnZVejHCc6',
            'ivanq.yu': '1FwH89xyniDgy3t6fCWrggLs22MnGPZ5K5',
            'zplace.yo': '1D6f2CvDRhPeEeBAcmqGt3X9z2CkLpmv2V',
            'coder.yo': '1CodEr7T9xNXSPcwbsvf5fHTqsixDMwDzL',
            'sands.yo': '1M6a1JXxdYWjNXZUuFk4SJdG5xWRRjBU4a',
            'gc.yo': 'reserved',
            'zeroup.balancer.yu': '1J8rt5k5QPLmAtRw5QAGmgKxi4qC7Lk166',
            'talk.balancer.yu': '15zr8fG5h9FZu6dt5CC9kQ1F7PMpiGu6Tm',
            'diy.balancer.yu': '1ApsfuUfnyJm19qZguDzzqj7se41Ggxzrt',
            'zeronet.balancer.yu': '1PxNZqJ3R3aUt171foqtzbhgZZ6JaggaAi',
            'military.balancer.yu': '14UqHSCXV6mF5UKcqg1cR7eg4uUPCSGZtP',
            'wiki.balancer.yu': '1NbzP9dgYhuY71bde9G1LuVGaCE69venzR',
            'flood.balancer.yu': '1GmoFQHVjYj4xDZZ5oMNnkGhvnfY1w3pPM',
            'blocklist.balancer.yu': '1HnyzU52qiJBW4LxHHzDJHiTceWrqMhh69',
            'pol.balancer.yu': '17ogL1aD6546DYwtb6UnMhF4hETaHBj6yD',
            'balancer.yu': '1MaQ4W5D6G52TpBfPACU9k9QcB1DxvHZ5v',
            'en.balancer.yu': '144W6itCd6jUqHDx5SDjbFaRdTnh4gRBBA',
            'mem.balancer.yu': '1BFvnf2QHmMsjZ8dnfT89WfW8mVX7FrQj7',
            'micro.balancer.yu': '1bmicr2VRXvcGZ8xE4bvtuhfvQRhfquAf',
            'infonesy.balancer.yu': '1GQkPB8mFgxH7GQQbkNPJtvRaZZpVi65u1',
            'info.balancer.yu': '18i1Ra9wePfmwhMCyhmLXXShxcSha5YAns',
            'tanzpol.balancer.yu': '1Anxiq4y8oJUBisB7igP8jKQNK1DPGiSR1',
            'bors.balancer.yu': '1AdhUSJLmpUE7Aq5nPBkUuxgcWaUfqtS84',
            'kaliningrad.balancer.yu': '1kgdheAxeoeK6R7MMmTV6neAihUYf9pJ1',
            'lor.yo': '1BpFtPez7mSiShtXfb4wPfMT1dZTuRybfZ',
            'airbase.yo': '1Jb5ZdmvTzVnHpa2hayjQk3H2kZgNVbmBb',
            'infonesy.yo': '1F4WVHDpQYxuJL6xEY3EZTYkZds9TTjVHC',
            'in.yu': '127.0.0.1',
            'of.yu': '127.0.0.1',
            'chan.yo': '1ADQAHsqsie5PBeQhQgjcKmUu3qdPFg6aA',
            'thunderwave.yo': '1CWkZv7fQAKxTVjZVrLZ8VHcrN6YGGcdky',
            'thundote.yo': '14PEBop2eFFvYFv2D3owaBpb98nsW7BCLH',
            'lightstar.yu': '1MdwanV12uDDiVsgrsifDFdSsigLRD9dzu',
            'zerolstn.yo': '1MQveQ3RPpimXX2wjW2geAGkNJ1GdXkvJ3',
            'xiamis.yo': '16KpwxZmLs4XzdJrjwBguxFNqhFmnMbZYQ',
            'xiamis.yu': '16KpwxZmLs4XzdJrjwBguxFNqhFmnMbZYQ',
            'h.yo': '19WTvkdL8rUnAqZNtg3XaPTiDsCAcc22eB',
            'kxonet.yo': '1GTVetvjTEriCMzKzWSP9FahYoMPy6BG1P',
            'ucadia.yo': 'ucadia',
            'fuck.yu': '127.0.0.1',
            'scru.yu': '127.0.0.1',
            'crazy.yo': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'crazy.yu': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'peerco.yo': '147RqkK3WP9FXJq4fXxSKjojYHw4Wrmy8A',
            'crazy.of': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'crazy.inf': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'crazy.zn': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'crazy.list': '1NtQvrYd8rJzQYP3j1snmi28mPn8wSXX4X',
            'tcjy.zn': '134Lv2kVHAynALDkFaP98mia1JKr4gxc3N',
            'emnet.zn': '16JySL65beXjeEjrhBQgosWg7tQwuNq93L',
            'vdmnet.zn': '1G5RZoqRh4NTwq6v9KF1AZ8woVfuNRFsrr',
            'mg0.zn': '1D6QfsBSZHmYWbuCxKG5ya31BiTczoZiES',
            'rexresearch.zn': '1D6QfsBSZHmYWbuCxKG5ya31BiTczoZiES',
            'timvanduin.zn': '1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',
            'vendelinek.yo': '1DBc3iFh94wdqmMhjBjh1wpYBc64wq2t4o',
            'fantpril.zn': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fantpril.yo': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fantpril.yu': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fantpril.of': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fantpril.inf': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fantpril.list': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'zn.zn': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'yo.yo': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'yu.yu': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'of.of': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'inf.inf': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'list.list': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'zilizili.zn': '127.0.0.1',
            'kaffie.it': '1A83ijw3boqTtqdLz8me7AqeK1nEK8yxeu',
            'kaffiene.it': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'kaffie.me': '1A83ijw3boqTtqdLz8me7AqeK1nEK8yxeu',
            'search.it': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'vendelinek.yu': '1DBc3iFh94wdqmMhjBjh1wpYBc64wq2t4o',
            'zerotalk.peerco.yo': '1LUrvRXuPxH5ENgWeCbhrpUYfxCwnFYFDJ',
            'zerome.peerco.yo': '1KjwPbyQTYgmLGJZZH25ZGGrCYrH2ULVVv',
            'myzeroblog.peerco.yo': '1Dtm44Lz74NzdPsEyG4rvXpC9rgojHeYGY',
            'youtube.peerco.yo': '18GzzygX2uFDxrHmV1kUfKpPPY2FDMz7YF',
            'helblindi.yu': 'reserved',
            'myzerowiki.peerco.yo': '1QK2jJrdG3qqgXidd9eW6d81TfLqGCXhoe',
            'google.yo': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'google.yu': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'google.of': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'google.inf': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'google.zn': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'google.list': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'o.of': '127.0.0.1',
            'pill.zn': '17p9vyd7FXm7FMgrirNeKKc3dXnp9dMD4q',
            'zerogamingtalking.yo': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.yo': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.yu': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.of': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.inf': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.zn': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalk.list': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerochatplus.yo': '1FbZQrfoXk4JkbtnAjt1FiyKTTAoECug7r',
            'zerositesplus.yo': '1NcCnWssDSyP7xja9rDMGrEwUWDdCSC9n2',
            'zerogamingtalkplus.yo': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'nickwawebtorrent.yo': '1HZBz6gsiPgYCJFD7MvBUZ5jKUt5Ag8dTF',
            'zerogamingtalkplus.yu': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalkplus.of': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalkplus.inf': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalkplus.zn': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'zerogamingtalkplus.list': '1J789oNvwoawy3xjfhfxEfvTeNk61JYf4Y',
            'tcjy.list': '127.0.0.1',
            'xn--ur0a479b.zn': '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
            'xkcd.yo': '1XKCDh5XeLm5eN4jM8b1Mk4wKrnUJxV12',
            'fant.yo': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fant.yu': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fant.of': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fant.inf': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fant.zn': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'fant.list': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'mayvaneday.yo': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'mayvaneday.yu': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'mayvaneday.of': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'mayvaneday.inf': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'mayvaneday.zn': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'mayvaneday.list': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'arkhello.zn': 'AHeLLoZZeps5VTxmKvuD49AS7X9ruNy5C8',
            'r.yu': 'r.yu',
            'r.yo': 'r.yo',
            'r.zn': 'r.zn',
            'ark.zn': 'ark.zn',
            'ark.list': 'ark.list',
            'audiobooks.zn': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'audiobooks.list': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'audiobooks.inf': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'audiobooks.of': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'mfs.zn': '1PSckqU7wo7oyALSWpePxUEmLpv3K6fwYb',
            'myzlog.zn': '1N7fJq4Ka65jpSpf9X2xf1YcCSqdCBdoc6',
            'fuk.yu': '1N7fJq4Ka65jpSpf9X2xf1YcCSqdCBdoc6',
            'guidovon.list': '1N7fJq4Ka65jpSpf9X2xf1YcCSqdCBdoc6',
            'a.zn': 'bicatpfsdeoco42pm5hcqsoo72x4gnfd6u7kpsamyve5c5ufuyea.b32.i2p',
            'doxbin.yo': '1DoxbinuaNEdDagSpPmbCEkKHB1FW9RzzJ',
            'zerodox.yo': '1DoxbinuaNEdDagSpPmbCEkKHB1FW9RzzJ',
            'zerodox.zn': '1DoxbinuaNEdDagSpPmbCEkKHB1FW9RzzJ',
            'doxbin.zn': '1DoxbinuaNEdDagSpPmbCEkKHB1FW9RzzJ',
            '08chan.yo': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '08chan.zn': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8chan.yo': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8chan.zn': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8ch.yo': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8ch.zn': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8.yo': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '8.zn': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '08.zn': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            '08.yo': '1DdPHedr5Tz55EtQWxqvsbEXPdc4uCVi9D',
            'millchan.yo': '1ADQAHsqsie5PBeQhQgjcKmUu3qdPFg6aA',
            'millchan.zn': '1ADQAHsqsie5PBeQhQgjcKmUu3qdPFg6aA',
            'mill.yo': '1ADQAHsqsie5PBeQhQgjcKmUu3qdPFg6aA',
            'mill.zn': '1ADQAHsqsie5PBeQhQgjcKmUu3qdPFg6aA',
            'hello.zn': '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
            'hello.yo': '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
            'me.yo': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'me.zn': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'fanto.yo': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'fanto.zn': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'fantoski.yo': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'fantoski.zn': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.yo': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.yu': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.of': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.inf': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.zn': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            '0.list': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.yo': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.yu': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.of': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.inf': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.zn': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'zero.list': '1FantoiURYdv9he66jhcMvmqy96oVEppVK',
            'porn.yo': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'porn.yu': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'porn.of': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'porn.inf': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'porn.zn': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'porn.list': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.yo': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.yu': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.of': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.inf': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.zn': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'sex.list': '1NZNtZQZHQRJXafvJpmY5jgqwRaCEZMsUc',
            'robloxo.of': 'bicatpfsdeoco42pm5hcqsoo72x4gnfd6u7kpsamyve5c5ufuyea.b32.i2p',
            'reasonsilovemyniece.list': '1N7fJq4Ka65jpSpf9X2xf1YcCSqdCBdoc6',
            'purpleblog.zn': 'http://127.0.0.1:43110/1LcAzdXV162HNrNFm77uVihYzWwthGM2vr/',
            'abooks.yo': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'abooks.yu': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'abooks.of': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'abooks.inf': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'abooks.zn': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'abooks.list': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'audiobooks.yo': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'audiobooks.yu': '1N77kxgd29cR8w9xt481JDJEtYdX1hCqAR',
            'kusoneko.yo': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'kusoneko.yu': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'kusoneko.of': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'kusoneko.inf': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'kusoneko.zn': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'kusoneko.list': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.yo': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.yu': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.of': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.inf': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.zn': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'blog.kusoneko.list': '1JT1qoXhg4JugdzXVnGcV6gaiXX3P4LwSj',
            'id.kusoneko.yo': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'id.kusoneko.yu': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'id.kusoneko.of': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'id.kusoneko.inf': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'id.kusoneko.zn': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'id.kusoneko.list': '1223AWa3Xikhn3q1d2UmCBx1NeJYx7tvE1',
            'tcmeta.yo': '15tek1Cg2VshZ7Hkxi97P27TYtdNpA5v5d',
            'obermui.yo': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            'obermui.inf': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            'obermui.zn': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            'obermui.list': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            'obermui.of': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            'obermui.yu': '15VuKHSRKpgyGAX87mCHYF2L95vad33SPY',
            '0sh.yo': '1GNTAKCimBv5xEnt7QvkDn8sTkEPj7ZYTL',
            'hk.yo': '1tADtGnuPx5wBbxP5dosqcAt82PitUmKZ',
            'furry.yo': '16Bbqixe9ABsyhueWLBKwQXEWdCF6ARoSQ',
            'regularflolloping.yo': 'null',
            'regularflolloping.yu': 'null',
            'regularflolloping.of': 'null',
            'regularflolloping.inf': 'null',
            'regularflolloping.zn': 'null',
            'regularflolloping.list': 'null',
            'zeronetia.yo': '12xozBV7dYskrNQ2G5srnzsTgStaX6Coph',
            'china.yo': '1CuGFe64XH3XLCiEPkSkwRprrfqZzdAjpp',
            '1024.yo': '1CuGFe64XH3XLCiEPkSkwRprrfqZzdAjpp',
            'usa.yo': '1CuGFe64XH3XLCiEPkSkwRprrfqZzdAjpp',
            'cn.yo': '1CuGFe64XH3XLCiEPkSkwRprrfqZzdAjpp',
            'chinese.yo': '1CuGFe64XH3XLCiEPkSkwRprrfqZzdAjpp',
            'dinucentra.yo': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'dinucentra.yu': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'dinucentra.of': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'dinucentra.inf': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'dinucentra.zn': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'dinucentra.list': '1AFwap4UEsTP5gvnzw5byRcTHGxSWCaRWA',
            'kxovid.yo': '14c5LUN73J7KKMznp9LvZWkxpZFWgE1sDz',
            'x.thunderwave.yo': '1LdeDdtifLpRwizQkzYmWWVuUpuDhrGz4f',
            'bigtable.yo': '1FxEVWeV5MjWXD1b4JtRcqj6piXvNbRjbJ',
            'bigtable.of': '1FxEVWeV5MjWXD1b4JtRcqj6piXvNbRjbJ',
            'spyware.inf': '1SpyWkvtp8bXz5x7K8EreCBt23tUaoXgz',
            'domenicotoscano.yo': '1Bo3BB2J9KipLxrkZ4RWBdTCoHgMwMXYR4',
            'cyberbuddah.yo': '1FH3PnVUkgYt1EaFnYDbw7V6QHSAofPPBX',
            'kave.yo': 'http://127.0.0.1:43110/1KN5zRytGbGqLNdemuoLC6gS44fwM9h38s/',
            'moab.list': 'http://127.0.0.1:43110/1LgqZfbtr6dukbjHdjWBEmmthq1shEv3y1/',
            'syncronite.yo': 'http://127.0.0.1:43110/15CEFKBRHFfAP9rmL6hhLmHoXrrgmw4B5o/',
            'app0.yo': 'http://127.0.0.1:43110/1E7wdLyfWBZAJoPtk7t7dxBAdVFDkWpKrX/',
            'live.list': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'live.of': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'live.zn': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'fashion.list': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'fashion.yo': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'fashion.zn': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'taobao.zn': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'taobao.list': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'amazon.list': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'amazon.yo': '166qaA2XQYrdEEyTBm2xgAN9AWEhtJrES3',
            'link.yo': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'link.yu': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'link.zn': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'link.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'link.inf': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'link.list': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.yo': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.yu': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.of': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.inf': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.zn': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'links.list': '1LinksxxdxzzmqSYH3nF2Diwq4xrdMK3MH',
            'start.list': '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
            'zerowikiuk.zn': '1Ewfx8U1QvPs61QoKvoCdx775CLv1xbC7',
            'js.zeroframe.zn': '1HJS6quLaqNLYxHVM9nL2rfmAsRvumqC1H',
            'py.zeroframe.zn': '178UMrEt8vxf5Z6LPxkrcWFPXPfD9XNNH7',
            'zero86.yo': '1z86z5jCaCQpgabfbQFJTLcKBLJdTtGYD',
            'dreamworks.yo': '1JBFNPrAGp1nQX6RsAN6oRqCfvtoeWoion',
            'id.emnet.zn': '15abcKj3RQn7LYDvTt55rc8ZmNwQLqHu5q',
            'lianna.yo': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'lianna.yu': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'lianna.of': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'lianna.inf': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'lianna.zn': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'lianna.list': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'javadoc12.yo': '12nKKTRJUmAvBL4WrNMAda5Sm58vNqjgU4',
            'streamz.yo': '1BTZh5pymEKzMYr3qgDtgr4dMmap77QvEs',
            'sogola.yo': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'schizo.yo': '15Aj7PkCPHfCHqNFUnEMoKBDwqHAJ7b9Q6',
            'wakaranai.yo': '17inszH5US5BfQMg66ChXSaT3oFKYAmGa1',
            'up.wakaranai.yo': '1VRSozLAjUfrdk8CN3coECyHckXqfmXww',
            'auth.wakaranai.yo': '1Evwaps3GXZJ6a78QBNaReHbVAucjZW2Dn',
            'mars.yo': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.yu': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.of': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.inf': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.zn': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.list': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.yo': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.yu': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.of': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.inf': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.zn': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'marusu.list': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'aytolis.yo': 'reserved',
            'aytolis.yu': 'reserved',
            'aytolis.of': 'reserved',
            'aytolis.inf': 'reserved',
            'aytolis.zn': 'reserved',
            'aytolis.list': 'reserved',
            'iodine.yo': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.yu': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.of': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.inf': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.zn': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.list': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'cetra.yo': 'reserved',
            'cetra.yu': 'reserved',
            'cetra.of': 'reserved',
            'cetra.inf': 'reserved',
            'cetra.zn': 'reserved',
            'cetra.list': 'reserved',
            'iodine.cetra.yo': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.cetra.yu': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.cetra.of': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.cetra.inf': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.cetra.zn': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'iodine.cetra.list': '16QJqCTaNceFbosyCP1deKqzWwT9BwYH3E',
            'mars.cetra.yo': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.cetra.yu': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.cetra.of': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.cetra.inf': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.cetra.zn': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'mars.cetra.list': '1MrwmugtdphP3CfYxXEgdefyjJV3LKMsW2',
            'systemspace.yo': '182vtVTeNuSt62iQRTiUbdV5VJhzdLrc1W',
            'testanothernet.yo': '1LCSoFMccgL3RuUkXGfvz42QwmWNQeSwxW',
            'testzeronet.yo': '1LCSoFMccgL3RuUkXGfvz42QwmWNQeSwxW',
            'cqega.list': '127.0.0.1',
            'akapen.yo': 'http://127.0.0.1:43110/1G6sNT5QbsMQ1i8M53bV9T1CBfPH3BqgW1',
            'syncronite2.yo': '15CEFKBRHFfAP9rmL6hhLmHoXrrgmw4B5o',
            'systemspace.yu': 'null',
            'systemspace.of': 'null',
            'systemspace.inf': 'null',
            'systemspace.zn': 'null',
            'systemspace.list': 'null',
            'erin.yo': 'reserved',
            'erin.yu': 'reserved',
            'erin.of': 'reserved',
            'erin.inf': 'reserved',
            'erin.zn': 'reserved',
            'erin.list': 'reserved',
            'null.yo': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'null.yu': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'null.of': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'null.inf': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'null.zn': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'null.list': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.yo': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.yu': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.of': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.inf': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.zn': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'grave.list': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.yo': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.yu': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.of': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.inf': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.zn': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'death.list': '1LiannAaMFCegAwz3dNUpRAC9Zj5XeAJjA',
            'vclv.yo': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'vclv.yu': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'vclv.of': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'vclv.inf': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'vclv.zn': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'vclv.list': '1MeeJWbbQHArbqD6UUHSjh9EVycvnTUBFa',
            'operapresto.yo': '1J3xKsavhVCXDA7VnZU2jsdY4Szbfa6AzN',
            'zeronetmobile.yo': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zeronetmobile.zn': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zeronetmobile.inf': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zeronetmobile.of': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zeronetmobile.yu': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zeronetmobile.list': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'tcmeta.zn': '15tek1Cg2VshZ7Hkxi97P27TYtdNpA5v5d',
            'xcwosjw.zn': '1KAEyHUkv7xxMToKcUrEp4sP6yNTgoPCT8',
            'xcwosjw.yo': '15nQ3ZjGyKNZf4iSLfQGgbxkZQjPp7Tdap',
            'esperanto.yo': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'esperanto.zn': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'eo.zn': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'eo.yo': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'talk.esperanto.yo': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'talk.esperanto.zn': '1YwB6u3f9TUfre8H9scXkbPyeuMaJSJio',
            'up.esperanto.yo': '12ZQUJ8yUka4h3gKNRq5LyCAH4tLxcTRWK',
            'up.esperanto.zn': '12ZQUJ8yUka4h3gKNRq5LyCAH4tLxcTRWK',
            'runpark.yo': '18M55ymFNbi6d2KSY7qTp7WuE7gJSyRaPW',
            'runpark.zn': '18M55ymFNbi6d2KSY7qTp7WuE7gJSyRaPW',
            'ru.zn': '1RuZntipLvXcLKFEjT6Fr7ZA3GuywYfr5',
            'ru.yo': '1RuZntipLvXcLKFEjT6Fr7ZA3GuywYfr5',
            'ihome.yo': '1Hw1Aa8JnQnUxs1fjBX4eT1vz7Ppow2NTU',
            'opennews.yo': '1Nowr5oVEdbU5ZTQBriRd2jJVj2vhsDJd4',
            'opennews.zn': '1Nowr5oVEdbU5ZTQBriRd2jJVj2vhsDJd4',
            'ailinux.inf': '67.210.147.173',
            'binchan2.yu': '1EiMAqhd6sMjPG2tznkkGXxhdwFBDdeqT9',
            'share.binchan2.yu': '1Dphm8Mth9WYN9fPm1yxj8Y4WhcKRhYXJJ',
            'gallery.binchan2.yu': '1D2C23aAoHeoJsvPjZZxS9bt3i93uRVfUP',
            'git.binchan2.yu': '13zzNGxEXDeLxHEGZdG3mE7G8dChf45LrV',
            'social.binchan2.yu': '1G9wPKCvqdzZVRzZizcsExhYufMpAxbh6U',
            'binchan.yu': '1EiMAqhd6sMjPG2tznkkGXxhdwFBDdeqT9',
            'gallery.binchan.yu': '1D2C23aAoHeoJsvPjZZxS9bt3i93uRVfUP',
            'git.binchan.yu': '13zzNGxEXDeLxHEGZdG3mE7G8dChf45LrV',
            'social.binchan.yu': '1G9wPKCvqdzZVRzZizcsExhYufMpAxbh6U',
            'share.binchan.yu': '1Dphm8Mth9WYN9fPm1yxj8Y4WhcKRhYXJJ',
            'srdsa.yo': 'http://127.0.0.1:43110/1Mv6N3tZD8txahjwRCKXWe5U86wWYzfnLB/',
            'strec.yo': '1D7ck8Ny1CrmBdWj3HgvkDj5azYqxfeRYG',
            'bunkerid.zn': '14NnbuAssiqZzYMwJJU3YQFVqg8FbXTTCH',
            'zeromeluna.yo': '1KKhuA3VHmMkbqK5zGfiXSG8cqPFts6TJH',
            'syncronite.zn': '15CEFKBRHFfAP9rmL6hhLmHoXrrgmw4B5o',
            'eternalword.inf': '1Mjd9zn88kNX1QEkFaq2MrWeMthnR15Fga',
            'moab.zn': '1LgqZfbtr6dukbjHdjWBEmmthq1shEv3y1',
            'app0.zn': '1E7wdLyfWBZAJoPtk7t7dxBAdVFDkWpKrX',
            'kave.zn': '1KN5zRytGbGqLNdemuoLC6gS44fwM9h38s',
            'zeromeluna.zn': '1KKhuA3VHmMkbqK5zGfiXSG8cqPFts6TJH',
            'kaftask.yo': '1PCceXgXcZqWZnxBvAJbUd5mnZE5FFx57t',
            'aassddff.yo': '157WDHELkDXEiejUonxka3UjetaMJi9bsK',
            'mu.aassddff.yo': '157WDHELkDXEiejUonxka3UjetaMJi9bsK',
            'pol.aassddff.yo': '17uqpm3ihgX955fqunzKWvbXytjYtUrxZd',
            'blog.kaftask.yo': '1EjXC6WCpvGarxhc762MKhevbCHgRepEdM',
            'qrcg.zn': '15mfebHgwT7DGkDqjg9Jc7PWGJdzLN3Keh',
            'lang.kaftask.yo': '15xWNd1GgK2rrk1xu1vrxyMHU5kmXUjAk1',
            'xmojtesting.yo': '47.97.230.153',
            'xerthes.yo': '1D6vw8r3vXbTsRWqzie9GHKZpFLLzXB6F7',
            'zmd.zn': '18QPAtqyoxriNcNAi4mkCHyoLENwTEbFyw',
            'taos.zn': '1NNGrbXrWjPVnV6pxkuKGngRP116VaAFtm',
            'sogola.yu': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'sogola.of': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'sogola.inf': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'sogola.zn': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'sogola.list': '15CTUyQvz1qT4dqjWT2Wmd4XbV5hesrMtL',
            'pinapplehead.yo': '1QB9CpRMkYQNmngfegWCKxmy7Tna5DjXAf',
            'merith.zn': '1JyMUCtShELPTKSF1HR3XUj4QEZx58Jcwy',
            'youngchina.yo': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'youngchina.yu': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'youngchina.of': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'youngchina.inf': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'youngchina.zn': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'youngchina.list': '19UYGrRyBASeTHSHvqZ9SYJTZxmnojA6kx',
            'zalex.yo': '1JChcgVVMqBy5fmN4er6afLhcoD7YzRDP6',
            'zalex.zn': '1JChcgVVMqBy5fmN4er6afLhcoD7YzRDP6',
            'ogame.yo': 'Me.ZeroNetwork.bit/?Profile/1KNmG5rJUGhgUJGFbLkv2B5isaqu9PrZqi/1KBkXs64bRMnZoTXzq5gdrsd1ZupSfMrwE/',
            'ogame.list': 'ogame.yo',
            'yeoldpaperblog.yo': '17aap8PVCLfDQYkmwPLrotnggjLEiNang4',
            'erg.yo': '18QTZ451KzvydQdCPS8KT4zob1hPw4zkRD',
            'yuzueabuilds.list': '1FBWiqA722gM8YqPqyXGvadskR77CAtBdm',
            'erkan.yo': '1HR2mJHeC1vs3XTTcX2X6BDcdRZZDNXZKV',
            'forum.yo': '17PEJfM9tdKs1JTxAMbcKzmYzrKJcUwMk5',
            'forum.inf': '17PEJfM9tdKs1JTxAMbcKzmYzrKJcUwMk5',
            'forum.zn': '17PEJfM9tdKs1JTxAMbcKzmYzrKJcUwMk5',
            'mokshanets.yo': '1MQ2e26P3v7Fb2rDPzNP83pfgERCtA92S5',
            'ifsplus.zn': '1BLnYeYMYhCQUiCVQKesJwa22Jzpcdd3Y6',
            'theciaproject.yo': '1HYzCVkN8pdQzdMdJptjSdEp6ADDP5XBZ4',
            'markdown.zn': '1J9bM4MbnTgsNcLWGnyKxT3m9jFQThxhkj',
            'kill.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'attraversamenti.yo': '1GBsk92HdiofXvoa7pxH2ak7jZNnR3svxk',
            'socks.list': '1HZLvwrcxebTNZv3q5bNHiB5QAkQy2DR7i',
            'ss13.zn': '1MADyUhyzDBxNn6Ww2NheL6Q2g4knpEV7',
            'nwo.inf': '1CooGPdLMarc56bF5mZgFQtqVBQbKjpm8e',
            'zeronet.zn': 'todo',
            'foxden.zn': 'http://127.0.0.1:43110/1DFnD5okB2BvXwPGtDY9KvCHtW1d8YYB9z/',
            'foxden.yo': '1LbrCJF2CEXzZZLvXyLH9Kt5msywU5AwFF',
            'astrr.yo': '1AV33QMZbXpkS9yU65qFwuykiLNo3rJs7M',
            'zeroseed1.yo': '104.171.122.70',
            'mix22.yo': '1246yWDRZVb85dexD5RU85uvaiuM6uZARv',
            'i-say-hi.yo': '1PNs1BYT8ZW2YnQL2wsCyVviiGTpdPBGBZ',
            'pc.yo': '161Aw5FXqB1WHzvQsQVfJooxK7YqmsT1BX',
            'videos.nwo.inf': '15Q1YyzZeAzL1PyyhDp8oNxQznsUPZ8eoP',
            'e.list': '1BTLVyQm5ugNdpWcEDMZK9giZnuFpsYqXV',
            'e.yo': '1BTLVyQm5ugNdpWcEDMZK9giZnuFpsYqXV',
            'truepi.inf': '1EKQALAZwz2LYKJGJmqjMcHFELjR8wA138',
            'covid19facts.inf': '1LUMdYx1yPsVuZthvmSr5RUKTbvuuc1A75',
            'truthircchat.zn': '1L1PnQwGfU6XinBcGv8ysCjduuzx2p7Huw',
            'sites.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'ratbrowser.yo': '14CFnCexfT3Xoj1SzWunNUNWDT7WqE3oUm',
            'bats.list': '19i7hXiRRz5vRqHmrUELKjzRofGPpAiFRv',
            'wasd1234.yo': '1JgMPiX13nD4C28ZY97EWjiVru9qFfiNgq',
            'astrr.zn': '1AV33QMZbXpkS9yU65qFwuykiLNo3rJs7M',
            'ifs.zn': '1BLnYeYMYhCQUiCVQKesJwa22Jzpcdd3Y6',
            'kopykate.zn': '1GPxQe1Qd76NpKNfCB2x1KnQLdZFuWFEAo',
            'zeroforums.zn': '1GutXgoFpA4B6DbCDsaSh9MzYf31iSfqf3',
            'zeroforum.zn': '1GutXgoFpA4B6DbCDsaSh9MzYf31iSfqf3',
            'pervertededucation.zn': '1PKW6qWBgVWRE3EkvJQaFv8uVpg2p1oYDQ',
            'trust.yo': '1PtFxzJ8NECkYQzziGWoEfzScD6NiEgqDY',
            'ruzero.zn': '1HKsGQWHbR33LjzqtoPfUBANXuYDy32hXp',
            'caoom.yo': '15art7pVw4pDaNZRugTxcMUEHPBC1mU2ZM',
            'z.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'szdcsdvszv.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'zheng.zn': '10.147.17.84',
            'zheng.yo': '10.147.17.84',
            'kaffiene.yo': '1Mr5rX9TauvaGReB4RjCaE6D37FJQaY5Ba',
            'chat.yo': '1Keke3V7Fn8bPt82QyhNHkv5gx5NnK9Umu',
            'chat.yu': '1Keke3V7Fn8bPt82QyhNHkv5gx5NnK9Umu',
            'dimitrisapostolou.yo': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'dimitrisapostolou.zn': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'dimitrisapostolou.yu': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'dimitrisapostolou.of': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'dimitrisapostolou.inf': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'dimitrisapostolou.list': '17u2fjXwkMKcUJkH9j4kXD2ha9pNsJPn1A',
            'zeronetx.yo': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'zeronetx.yu': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'zeronetx.zn': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'zeronetx.of': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'zeronetx.inf': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'zeronetx.list': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'moviebuzz.zn': '1HKGxbiYxmX68PcrLLKpyMVKE1SUdNfqRZ',
            'sh.zn': '1Ciwsxcy7XjH2EBzhDTfMExjTiBK4kYzeZ',
            'alexandr-monada.yo': '127.0.0.1',
            'zerotalkx.yo': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zerotalkx.yu': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zerotalkx.of': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zerotalkx.inf': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zerotalkx.zn': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'zerotalkx.list': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'compiler.yo': '14nKr6su4QvsVZNZAKt2YMTYQr755EkYys',
            'monkic.yo': '1vwuCChcRPJ6D1YqTK5UFmv8UWQAn6ptN',
            'about.yo': '19scCr6HceYeuGKADK4Qtz1USjNmUHqF5B',
            'natewrench.yo': '1AQ3tZW4GCzoiR7FzdbwYMHW4bQgyJCYkr',
            'natewrench.list': '1AQ3tZW4GCzoiR7FzdbwYMHW4bQgyJCYkr',
            'scribe.yo': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'scribe.zn': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'scribe.list': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'scribe.inf': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'scribe.of': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'scribe.yu': '1SCribeHs1nz8m3vXipP84oyXUy4nf2ZD',
            'threadit.yo': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'threadit.zn': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'threadit.list': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'threadit.inf': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'threadit.of': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            'threadit.yu': '15UYrA7aXr2Nto1Gg4yWXpY3EAJwafMTNk',
            '3dfxglide.yo': '13dfxGLmVKbiK25MFJHgR9Nr1hmGAGjWbP',
            'ratbrowser.zn': '1NFjL6KmJYwojYMat8RXCPo2JWMvNzfHAk',
            'merlin.of': '1Mer3VhxoePJN7tqHvEAgMCuq4LLtU1N4k',
            'disable-donate.yo': '1JFuiZvpL9NKoggbW6M5GWeZWoucNvRLTX',
            'irantalk.zn': '1AS355T7MGApApoBeE9JgxvvvDxf33Eyh1',
            'farsiroom.zn': '1Ebc6bHBq7Ewgczuc9pqYh2jPFeC7vAwL7',
            'xerome.zn': '1JgcgZQ5a2Gxc4Cfy32szBJC68mMGusBjC',
            'darkasnight.zn': '1DbaVzv27GUx2LqXnMdrQCtzKcyS2zxdEd',
            'zeronetpersian.yo': 'http://127.0.0.1:43110/1NLMuTNWRKmfntZXmYyJWnoP85RHuzAWZW/',
            'zeronetpersian.zn': 'http://127.0.0.1:43110/1NLMuTNWRKmfntZXmYyJWnoP85RHuzAWZW/',
            'musthave.zn': '1LgjqcYMyhdEE81QZPCsBNnSKk8nzTg7tZ',
            'free-zone.zn': '17VhUiHjg34DfT2mZnCVr1RmU6sEJmscV2',
            'fitmisc.zn': '15Z5QHc3ajeHPGNHkWoBaCqpybe48A9meB',
            'files.free-zone.zn': '1DF26VGtsJrmNLfRfCqBbH4v4Godegh6B2',
            'fa.zn': '13dpeEht6Ztbu3EpUVUyj9eLJwPJLiPrT1',
            'me.fa.zn': '1JgcgZQ5a2Gxc4Cfy32szBJC68mMGusBjC',
            'talk.fa.zn': '1AS355T7MGApApoBeE9JgxvvvDxf33Eyh1',
            'hub.fa.zn': '13YccBekYK3S5LE1sva2wE2cUo6tk3BaWV',
            'chat.fa.zn': '1Ebc6bHBq7Ewgczuc9pqYh2jPFeC7vAwL7',
            'blog.fa.zn': '1DbaVzv27GUx2LqXnMdrQCtzKcyS2zxdEd',
            'fa.yo': '13dpeEht6Ztbu3EpUVUyj9eLJwPJLiPrT1',
            'toldyouso.yo': 'toldyouso',
            'toldyouso.yu': 'toldyouso',
            'toldyouso.zn': 'toldyouso',
            'toldyouso.list': 'toldyouso',
            'test.ivanq.yu': 'test3',
            'letsgo.zn': '1ETsGoB5HjhVV3r2MNtcKox8rcjtsLz77T',
            'eddyle.yo': '1KxakekWHCku9xeUZPfHXcsRqXCKZZrnJe',
            '0netfarsi.zn': '1NLMuTNWRKmfntZXmYyJWnoP85RHuzAWZW/',
            '0netfa.yo': '1NLMuTNWRKmfntZXmYyJWnoP85RHuzAWZW',
            'parishan.zn': '17mid9iAabJ7SKSGL6LiaABmbmesA1vohB',
            'znfa.zn': '1NLMuTNWRKmfntZXmYyJWnoP85RHuzAWZW',
            '0index.inf': '1C3XRn6awmJvTCwTgTE88YzAzTfV8xFk9V',
            '0index.zn': '1it4GjtNTkrFDX5pSXToqLYbEfxfqvPSR',
            '00.zn': '1C3XRn6awmJvTCwTgTE88YzAzTfV8xFk9V',
            '0netmirror.yo': '1LRb9GK6z3VEYwxtANCsszm3XDmQV3XT2G',
            'bbs.runpark.zn': '129Lxtnj45HkSnV9cGWmpBMNXffbeiG5RY',
            'bbs.runpark.yo': '129Lxtnj45HkSnV9cGWmpBMNXffbeiG5RY',
            'yaddasht.list': '1B5t5iPNdFvoegP3Z53tFfUHnw2wJp27iz',
            'iranproxy.yo': '1LKSyzSjccKWjgb8hNzALbYi8Q1sXCnmhN',
            'atlasft.yo': '1MAMEA17CHmFVeAWYmfBt6PWupozhufwic',
            'meme-beta.yo': '155xNWmKGzHqmy278pFK4NXRNDfaeGoHVU',
            '1heal.yo': 'https://1heal.org',
            '1heal.yu': 'https://1heal.org',
            '1heal.zn': 'https://1heal.org',
            '1heal.list': 'https://1heal.org',
            'kraken.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'krn.inf': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'ultravoxtalk.yo': '1DmPuYVLGCmqguvoFFkUcogBu12weot56G',
            'test00110011.yo': '1HELLoE3sFD9569CLCbHEAVqvqV7U2Ri9d',
            'iran.inf': '1Lhiv2fCT6sB33A7p2GJCresA8aEZ84pHw',
            'teamsds.yo': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'teamsds.yu': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'teamsds.of': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'teamsds.inf': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'teamsds.zn': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'teamsds.list': '1NBtw2bYJw6TCr6CJwfbi3a7C1p61hmCVg',
            'madari.yo': '16QUxodsgcaRbJQtmKAUtNooF34Rxyg8EA',
            'madari.inf': '16QUxodsgcaRbJQtmKAUtNooF34Rxyg8EA',
            'yoxel.yo': '12kU1Esb8cTdPJkkZRCXkTcNExihFAzbmQ',
            'proxy.yo': '15V6KSMNc7X3hofZHy64s5LHtbVgrpYzSu',
            'paperhatsociety.zn': '1AbmBjhZ18UAMHMMhwp7LK9zrqAEKJ7iKA',
            'miceweb.yo': '1MiceWebdn35s6pUd3EM54uNveUJNSHsMr',
            'miceweb.zn': '1MiceWebdn35s6pUd3EM54uNveUJNSHsMr',
            'miceweb.inf': '1MiceWebdn35s6pUd3EM54uNveUJNSHsMr',
            'denny.inf': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'hot.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'best.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'free.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'travel.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'cheap.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'ads.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'adblock.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'adult.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'file.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'top.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'domain.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'opusx.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'bucket.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'denny.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'my.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'your.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'private.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'tracker.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'proxy.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'wish.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'free.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'voip.inf': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'voip.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'todo.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'my.inf': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'ma.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'lots.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'freeware.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'software.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'apps.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'mostwanted.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'task.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'freebies.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'coupons.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'makeuse.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'way.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'e.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'code.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'get.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'hey.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'zeronet.inf': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'big.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'small.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'tiny.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'giant.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'huge.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'monster.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'friend.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'friends.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'domain.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'site.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'url.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'favorites.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'bookmarks.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'hidden.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'shopping.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'dingdong.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'my.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'co.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'com.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'co.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'com.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'org.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'org.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'net.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'net.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'shared.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'co.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'com.zn': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'bump.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'joy.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'name.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'short.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'best.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            '18.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            '16.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            '21.yo': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'made.of': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'cam.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'cams.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'webcam.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'webcams.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'sexcam.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'sexcams.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'a.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'secret.list': '1NAMEz7stUPZErkV1d3yLkVWQFa4PTqDNv',
            'nya.yo': '1BuUkkXsAzPHdEK78nxNZjiVcvUS12LBks',
            'galactichan.yo': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'galactichan.yu': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'galactichan.zn': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'galactichan.of': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'galactichan.inf': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'galactichan.list': '19HKdTAeBh5nRiKn791czY7TwRB1QNrf1Q',
            'electroperra.yo': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'electroperra.list': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'electroperra.yu': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'electroperra.of': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'electroperra.inf': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'electroperra.zn': '1EoakGCUsHZrjMe9V86PBktkzn8T7LK2rG',
            'aznet.zn': '1Gwm9zviPznj2BuvmS2sHko9m3uupW27JR'
        };
  
    def load_cache(self):
        if hasattr(self, "zero_cache"):
           return

        self.cache_file_path = os.path.dirname(os.path.abspath(__file__)) + "/ZeroNameExPlugin.json"
        if not os.path.isfile(self.cache_file_path):
           zero_cache = {
              "domains": {},
              "yo_domains": self.get_yo_domains(),
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
        self.zero_yo_domains = self.zero_cache["yo_domains"]
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
              new_domains.update(self.zero_yo_domains)
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
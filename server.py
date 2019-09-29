#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/7 下午2:17
# @Author  : Stardustsky
# @File    : test_server.py
# @Software: PyCharm
import os
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from core import main
import json
import numpy as np
import cv2


class IndexHandler(tornado.web.RequestHandler):

    def get(self):

        try:
            pass
        except:
            self.render("index.html",market="",)
        self.render("index.html", cap_info="", )





    def post(self):
        try:
            cap_dict = dict()
            cap_type = self.get_query_arguments("cap_type")
            img_arr = self.request.files["image"][0]
            img = img_arr['body']
            file_np_array = np.fromstring(img, np.uint8)
            img = cv2.imdecode(file_np_array, cv2.IMREAD_COLOR)
            cap_code = main(img, cap_type="401")
            cap_dict['code'] = cap_code
            cap_dict = json.dumps(cap_dict)
            self.render("capapi", cap_info=cap_dict)
        except Exception as e:
            cap_dict['code'] = "-1"
            cap_dict = json.dumps(cap_dict)
            self.render("capapi", cap_info=cap_dict)




class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
        ]

        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "login_url": "/"
        }

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    port = 9999
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
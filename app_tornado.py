# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web

class H(tornado.web.RequestHandler):
    def get(self): self.write("Tornado Chat Active")

app = tornado.web.Application([(r"/", H)])
if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

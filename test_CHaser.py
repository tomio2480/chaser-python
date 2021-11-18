#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import StringIO
import contextlib
import sys
import unittest
import CHaser


class contextlib_redirect_stdin(contextlib._RedirectStream):
    """
    標準入力を横取りするためのおまじない
    """
    _stream = "stdin"


class TestCHaser(unittest.TestCase):
    """
    contextlibを使って標準入力・出力・エラーを横取りし
    Clientの起動パラメーターを渡してのテストを行う
    """
    def tearDown(self) -> None:
        """
        sys.argvはテストケースをまたいで残るため都度リセットする
        """
        del sys.argv[1:]
        return super().tearDown()

    def test_noargs(self):
        """
        コマンドライン引数なしでClientを初期化したテストケース
        StringIOを使って input 関数に入力を行う
        """
        buf_in = StringIO()
        buf_in.write("9999\n")
        buf_in.write("MyName\n")
        buf_in.write("0.0.0.0\n")
        buf_in.seek(0)
        buf_out = StringIO()
        buf_err = StringIO()
        with contextlib.redirect_stdout(buf_out), \
             contextlib.redirect_stderr(buf_err), \
             contextlib_redirect_stdin(buf_in):
            try:
                client = CHaser.Client()
                self.assertEquals(9999, client.port)
                self.assertEquals("MyName", client.name)
                self.assertEquals("0.0.0.0", client.host)
            except ConnectionRefusedError:
                pass

    def test_default_values(self):
        """
        inputに空文字列を送った場合のテストケース
        """
        buf_in = StringIO()
        buf_in.write("\n")
        buf_in.write("\n")
        buf_in.write("\n")
        buf_in.seek(0)
        buf_out = StringIO()
        buf_err = StringIO()
        with contextlib.redirect_stdout(buf_out), \
             contextlib.redirect_stderr(buf_err), \
             contextlib_redirect_stdin(buf_in):
            try:
                client = CHaser.Client()
                self.assertEquals(2009, client.port)
                self.assertEquals("User1", client.name)
                self.assertEquals("127.0.0.1", client.host)
            except ConnectionRefusedError:
                pass

    def test_argv(self):
        """
        コマンドライン引数を渡してClientを初期化したテストケース
        """
        sys.argv.append("-p")
        sys.argv.append("2010")
        sys.argv.append("-n")
        sys.argv.append("User2")
        sys.argv.append("-h")
        sys.argv.append("127.0.0.1")
        buf_in = StringIO()
        buf_out = StringIO()
        buf_err = StringIO()
        with contextlib.redirect_stdout(buf_out), \
             contextlib.redirect_stderr(buf_err), \
             contextlib_redirect_stdin(buf_in):
            try:
                client = CHaser.Client()
                self.assertEquals(2010, client.port)
                self.assertEquals("User2", client.name)
                self.assertEquals("127.0.0.1", client.host)
            except ConnectionRefusedError:
                pass

    def test_invalid_argv(self):
        """
        不正なコマンドライン引数を渡したテストケース
        """
        sys.argv.append("-a")
        buf_in = StringIO()
        buf_out = StringIO()
        buf_err = StringIO()
        with contextlib.redirect_stdout(buf_out), \
             contextlib.redirect_stderr(buf_err), \
             contextlib_redirect_stdin(buf_in):
            try:
                CHaser.Client()
            except SystemExit:
                expect = "option -a not recognized\n"
                self.assertEquals(expect, buf_out.getvalue())


if __name__ == '__main__':
    unittest.main()

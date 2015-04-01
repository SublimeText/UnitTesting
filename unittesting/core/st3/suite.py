# This file is based on the previous work from Kay-Uwe Lorenz in the plugin
# sublimepluginunittestharness with the following License
#
# Copyright (c) 2013, Kay-Uwe (Kiwi) Lorenz <kiwi@franka.dyndns.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from unittest import suite


class DeferrableTestSuite(suite.TestSuite):

    r'''Deferrable test suite.

    Run method is basically a copy from suite.TestSuite, but it is a
    generator.  If a generator is returned by a test, there is entered
    a consumer loop and for each step there is done a step here.
    '''

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            if result.shouldStop:
                break

            if suite._isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                yield
                self._handleModuleFixture(test, result)
                yield
                self._handleClassSetUp(test, result)
                yield
                result._previousTestClass = test.__class__

                if (getattr(test.__class__, '_classSetupFailed', False) or
                        getattr(result, '_moduleSetUpFailed', False)):
                    continue

            if not debug:
                deferred = test(result)

                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x

            else:
                deferred = test.debug()

                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x

            yield

        if topLevel:
            self._tearDownPreviousClass(None, result)
            yield
            self._handleModuleTearDown(result)
            yield
            result._testRunEntered = False

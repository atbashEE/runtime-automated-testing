/*
 * Copyright 2022-2023 Rudy De Busscher (https://www.atbash.be)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package be.rubus.runtime.testing.logging;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Date;


@Path("/logging")
public class LoggingTriggerResource {

    @GET
    public String startLogging() {
        new Thread(new LoggingRunnable(5000L)).start();
        return "Logging started ";
    }

    @GET
    @Path("/flood")
    public String startLoggingFlood() {
        new Thread(new LoggingRunnable(10L)).start();
        return "Logging flood started ";
    }

    private static class LoggingRunnable implements Runnable {

        private static final Logger LOGGER = LoggerFactory.getLogger(LoggingRunnable.class);

        private final long waitTime;

        public LoggingRunnable(long waitTime) {
            this.waitTime = waitTime;
        }

        public void run() {
            while (true) {
                LOGGER.info("Logging entry " + new Date());
                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}

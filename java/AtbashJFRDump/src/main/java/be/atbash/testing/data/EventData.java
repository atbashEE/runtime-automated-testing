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
package be.atbash.testing.data;

import jdk.jfr.consumer.RecordedEvent;

import java.time.Instant;

public class EventData {

    private final Instant startTime;
    private final String message;

    public EventData(RecordedEvent event) {
        startTime = event.getInstant("startTime");
        message = event.getString("message");
    }

    public Instant getStartTime() {
        return startTime;
    }

    public String getMessage() {
        return message;
    }


}

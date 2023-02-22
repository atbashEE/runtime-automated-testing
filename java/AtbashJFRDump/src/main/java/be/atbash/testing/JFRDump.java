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
package be.atbash.testing;

import be.atbash.json.JSONValue;
import be.atbash.testing.data.EventData;
import be.atbash.testing.data.JFRData;
import jdk.jfr.consumer.RecordedEvent;
import jdk.jfr.consumer.RecordingFile;

import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;

public class JFRDump {

    public static void main(String[] args) throws IOException {
        String filename = args[0];
        String eventName = "be.atbash.runtime.event";

        JFRData jfrData = new JFRData();

        try (RecordingFile recordingFile = new RecordingFile(Path.of(filename))) {
            while (recordingFile.hasMoreEvents()) {

                RecordedEvent event = recordingFile.readEvent();

                if (eventName.equals(event.getEventType().getName())) {
                    EventData eventData = new EventData(event);

                    jfrData.addEvent(eventData);
                }

            }

        }

        JSONValue.registerWriter(Instant.class, new InstantWriter());
        String json = JSONValue.toJSONString(jfrData);
        System.out.println(json);
    }
}

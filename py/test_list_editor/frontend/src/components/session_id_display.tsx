// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { getUserSessionToken } from "../utils/user_session";

export function SessionIdFloater() {
  const { user_id: userId, session_id: sessionId } = getUserSessionToken();
  return (
    <div>
      <span
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          zIndex: 3100,
          color: "lightgray",
        }}
      >
        Session: {sessionId}, User: {userId}
      </span>
    </div>
  );
}

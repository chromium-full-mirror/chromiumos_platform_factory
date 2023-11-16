// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { v4 as uuid } from "uuid";

const USER_TOKEN_STRING = "editor_user_token";
const SESSION_TOKEN_STRING = "editor_session_token";

/**
 * Represents the tokens used for identifying a user and their session.
 */
export interface UserSessionToken {
  /**
   * The unique identifier for the user, stored in localStorage.
   */
  user_id: string;
  /**
   * The unique identifier for the session, stored in sessionStorage.
   */
  session_id: string;
}

/**
 * Retrieves or generates unique tokens for user and session identification.
 *
 * This function retrieves the user's token from localStorage and the session token from
 * sessionStorage. If either token does not exist, it generates a new UUID token and stores
 * it in the respective storage.
 *
 * The user token would remain the same across different tabs. However, the session token would be
 * different across tabs.
 *
 * @return {UserSessionToken} An object containing `user_id` and `session_id` tokens.
 */
export function getUserSessionToken(): UserSessionToken {
  const userToken = localStorage.getItem(USER_TOKEN_STRING);
  const sessionToken = sessionStorage.getItem(SESSION_TOKEN_STRING);
  if (userToken === null) {
    localStorage.setItem(USER_TOKEN_STRING, uuid());
  }
  if (sessionToken === null) {
    sessionStorage.setItem(SESSION_TOKEN_STRING, uuid());
  }
  return {
    user_id: localStorage.getItem(USER_TOKEN_STRING) as string,
    session_id: sessionStorage.getItem(SESSION_TOKEN_STRING) as string,
  };
}

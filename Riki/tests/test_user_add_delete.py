"""Test cases for accessing new APIs for creating and deleting user accounts in the wiki system"""
import unittest
from tests import WikiBaseTestCase
from csc440_albertm1_stage_a.user_createdelete import delete_users_by_role

class TestAccountFeatures(WikiBaseTestCase):

        # Tests to confirm the access of new API pages

        """test_get_login attempts to load login interface page."""

        def test_get_login(self):
                response = self.app.get('/user/login/', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('Login', response.data)

        """test_login attempts to login to wiki system. Necessary step because if we can't login, there is likely something
        wrong with the system, and we won't be able to test the delete user API"""

        def test_login(self):
            self.app.get('/user/login/', follow_redirects=True)
            response = self.login_helper("name", "1234")
            #print(response.data) # Can be used to view redirected page contents of the response
            self.assertEqual(response.status_code, 200)

        """test_create_user creates a new user for the user.json database file. It seems like a simple test, but was
        surprisingly troublesome during implementation stages, due to multiple configuration factors and app context
        issues. It works quite well though!"""

        """Note, without a "Delete User" test active, you will have to change the new user name each time, otherwise
        this test won't do anything (even though it may look like it succeeded) because the user_create API will reject
        the pre-existing username."""

        def test_create_user(self):
            self.app.get('/user/create/', follow_redirects=True)
            response = self.user_create_helper("testing", "123")
            #print(response.data) # Can be used to view redirected page contents of the response
            self.assertEqual(response.status_code, 200)
            self.app.get('/user/login/', follow_redirects=True)
            responseL = self.login_helper("testing", "123")
            self.assertEqual(responseL.status_code, 200)

        """test_create_user_fail should fail to create the user 'testing' because such user already exists
        in the wiki system. You can't have the same wiki user name. We'll test if this process failed by attempting to
        log in with the same username, but the attempted new password"""

        def test_create_user_fail(self):
            self.app.get('/user/create/', follow_redirects=True)
            response = self.user_create_helper("testing", "12345")
            print response.data
            assert "Failed" in response.data
            self.app.get('/user/login/', follow_redirects=True)
            responseL = self.login_helper("testing", "12345")
            print(responseL.data)
            self.assertEqual(responseL.status_code, 200)
            #print(responseL.data) # Can be used to view redirected page contents of the response

        """test_delete_user attempts to delete the user created from the previous test_create_user unittest"""

        def test_delete_user(self):
            self.app.get('/user/login/', follow_redirects=True)
            response = self.login_helper("name", "1234")
            assert "Login successful" in response.data
            self.app.get('/user/delete/testing', follow_redirects=True)
            response1 = self.user_delete_helper("testing", "123")
            self.assertEqual(response1.status_code, 200)
            self.app.get('/user/login/', follow_redirects=True)
            response = self.login_helper("testing", "123")
            print(response.data)
            self.assertEqual(response.status_code, 200)

        """test_delete_users_by_role attempts to delete all users from users.json file that have the "test" role.
        Note that user entries with "test" role are manually added before running this test."""

        def test_delete_users_by_role(self):
            self.app.get('/user/login/', follow_redirects=True)
            response = self.login_helper("name", "1234")
            assert "Login successful" in response.data
            username1 = "roleDeleteDummy01"
            username2 = "roleDeleteDummy02"
            response = delete_users_by_role("C:\Users\Matt\PycharmProjects\Riki\user\users.json", "test")
            assert username1 not in response
            assert username2 not in response



if __name__ == '__main__':
        unittest.main()

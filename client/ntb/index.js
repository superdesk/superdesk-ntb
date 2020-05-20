import angular from 'angular';

export default angular.module('ntb', ['superdesk.core.auth.login'])
    .run(['$templateCache', ($templateCache) => {
        // replace core login template with custom
        console.info('ntb');
        $templateCache.put(
            'scripts/core/auth/login-modal.html',
            require('./views/login-modal.html'),
        );
    }]);
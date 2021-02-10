import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [{id: 'auto-tagging-widget', load: () => import('superdesk-core/scripts/extensions/auto-tagging-widget/dist/src/extension').then(res => res.default)}],
        {},
    );
});

export default angular.module('ntb', [])
    .run(['$templateCache', ($templateCache) => {
        // replace core login template with custom
        $templateCache.put(
            'scripts/core/auth/login-modal.html',
            require('./views/login-modal.html'),
        );
    }]);

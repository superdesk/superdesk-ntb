import {startApp} from 'superdesk-core/scripts/index';
import autoTaggingWidget from 'superdesk-core/scripts/extensions/auto-tagging-widget/dist/src/extension';

setTimeout(() => {
    startApp([
        autoTaggingWidget,
    ]);
});

export default angular.module('ntb', [])
    .run(['$templateCache', ($templateCache) => {
        // replace core login template with custom
        $templateCache.put(
            'scripts/core/auth/login-modal.html',
            require('./views/login-modal.html'),
        );
    }]);

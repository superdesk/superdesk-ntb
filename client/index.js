import {startApp} from 'superdesk-core/scripts/index';
import planningExtension from 'superdesk-planning-extension';

setTimeout(() => {
    startApp(
        [planningExtension],
        {},
    );
});

export default angular
    .module('ntb.superdesk', []);
